from flask_restful import  fields


post_serializer={
    "id":fields.Integer,
    "title":fields.String,
    'body':fields.String,
    "image":fields.String,
    "created_at":fields.DateTime,
    "updated_at":fields.DateTime,
    }

