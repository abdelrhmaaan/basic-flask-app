from flask import Flask,render_template,request ,redirect ,url_for , send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restful import Api, Resource , marshal_with
from serializers import post_serializer
from parsers import post_request_parser




app = Flask(__name__) # create instance from flask to the current file
api = Api(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab1.sqlite"
db.init_app(app)

app.config['UPLOAD_FOLDER'] = 'media'



# post table 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text)
    image = db.Column(db.String(255))  
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    @classmethod
    def get_all_posts(cls):
        return cls.query.all()
    def get_image_url(self):
        return url_for('upload',filename=f'{self.image}')


@app.route('/uploads/<filename>',endpoint='upload')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


class PostListResource(Resource):
    def get(self):
        posts = Post.query.all()
        post_list = []
        for post in posts:
            post_list.append({
                'id': post.id,
                'title': post.title,
                'body': post.body,
                'image': post.image,
                'created_at': post.created_at,
                'updated_at': post.updated_at
            })
        return post_list
    @marshal_with(post_serializer)
    def post(self):
        # accept request parameters
        post_args=post_request_parser.parse_args()
        new_post = Post(
            title=post_args['title'],
            body=post_args['body'],
            image=post_args['image'],
        )
        print(new_post)
        db.session.add(new_post)
        db.session.commit()
        return  new_post, 201


class PostResource(Resource):
    @marshal_with(post_serializer)
    def get(self, post_id):
        post =Post.query.get(post_id)
        return post, 200
    
    @marshal_with(post_serializer)
    def put(self, post_id):
        post =Post.query.get(post_id)
        post_args = post_request_parser.parse_args()
        post.title=post_args['title']
        post.image = post_args['image']
        post.body = post_args['body']
        db.session.add(post)
        db.session.commit()
        return post
    
    def delete(self, post_id):
            post = Post.query.get_or_404(post_id)
            db.session.delete(post)
            db.session.commit()
            return  'no content', 204


api.add_resource(PostListResource, '/postsapi')
api.add_resource(PostResource,'/postapi/<post_id>')

# routes 
@app.route('/',endpoint='home')
def index():
    posts = Post.get_all_posts()
    return render_template('pages/index.html',posts=posts)

@app.route('/aboutus',endpoint='aboutus')
def about():
    return render_template('pages/about.html')

@app.route('/contactus',endpoint='contactus')
def contact():
    return render_template('pages/contact.html')


#buttons 
@app.route('/show/<id>',endpoint='show')
def show(id):
    post = Post.query.get_or_404(id)
    print(post.get_image_url)
    return render_template('pages/show.html',post=post)

@app.route('/delete/<id>',endpoint='delete')
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/create',methods=['GET','POST'],endpoint='create')
def create():
    if request.method == 'POST' :
        print(request.form)
        new_post = Post(**request.form)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('pages/create.html')

@app.route('/edit/<int:id>',methods=['GET','POST'],endpoint='edit')
def edit(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST' :
        post.title = request.form['title']
        post.body = request.form['body']
        post.image = request.form['image']
        if post.title and post.body :
            db.session.commit()
            return redirect(url_for('show',id=id))
    return render_template('pages/edit.html',post=post)



if __name__ == '__main__':
    app.run(debug=True)