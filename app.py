# !!! Test all routes in Postman !!!
# Ipdb is triggered when a route housing a set_trace() is hit in postman.
# Slack Thompson repo if you are still having issues. 
# Schedule another one on one. 

from flask import make_response, jsonify, request, session, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource
from flask_migrate import Migrate
import ipdb
import datetime 
from marshmallow_sqlalchemy import SQLAlchemySchema

from config import app, db, api, ma
from models import User, BlogPost, Comment, Category, db
from sqlalchemy.exc import IntegrityError
from marshmallow import fields


class UserSchema(ma.SQLAlchemySchema):
    id = fields.Int(dump_only=True)

    class Meta:
        model = User
    username = ma.auto_field()
    bio = ma.auto_field()
    blog_posts = ma.auto_field()
    comments = ma.auto_field()


    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "user_by_id",
                values=dict(id="<id>")),
            "collection": ma.URLFor("users"),
        }
    )

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class BlogPostSchema(ma.SQLAlchemySchema):
        id = fields.Int(dump_only=True)
    
        class Meta:
            model = BlogPost
    
        title = ma.auto_field()
        blog_content = ma.auto_field()
        publication_date = ma.auto_field()
        edited_at = ma.auto_field()
        user_id = ma.auto_field()
    
        url = ma.Hyperlinks(
            {
                "self": ma.URLFor(
                    "blog_post_by_id",
                    values=dict(id="<id>")),
                "collection": ma.URLFor("blog_posts"),
            }
        )

blog_post_schema = BlogPostSchema()
blog_posts_schema = BlogPostSchema(many=True)

class CommentSchema(ma.SQLAlchemySchema):
    id = fields.Int(dump_only=True)
        
    class Meta:
        model = Comment
        
    comment_content = ma.auto_field()
        
    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "comment_by_id",
                values=dict(id="<id>")),
            "collection": ma.URLFor("comments"),
        }
    )

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

class CategorySchema(ma.SQLAlchemySchema):
    id = fields.Int(dump_only=True)
            
    class Meta:
        model = Category
            
    name = ma.auto_field()
    description = ma.auto_field()
            
    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "category_by_id",
                values=dict(id="<id>")),
            "collection": ma.URLFor("categories"),
        }
    )

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

# Login and Signup are both adding users to the db. Both generate 500 errors. 

class Signup(Resource):
    def post(self):

        # password validations 

        request_json = request.get_json()

        username=request_json['username']
        password=request_json['password']
        bio=request_json['bio']

        user = User(
            username=username,
            bio=bio
        )
        # ipdb.set_trace()
        user.password_hash = password

        try: 
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            return user.to_dict(), 201
            
        
        except IntegrityError: 

            return {'error': "422 Unprocessable Entity"}, 422

class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return user.to_dict(), 200
        return {'error': '401 Unauthorized'}, 401

class Login(Resource):
    def post(self):

        request_json = request.get_json()

        username = request_json['username']
        password = request_json['password']


        user = User.query.filter(User.username == username). first()

        if user: 
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200
            return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error': '401 Unauthorized'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Signup, '/CheckSession', endpoint='check_session')
api.add_resource(Signup, '/login', endpoint='login')
api.add_resource(Signup, '/logout', endpoint='logout')

def expiration_date(delay):
    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(days=delay)
    return expire_date

@app.route("/cookies", methods=['GET'])
def cookies():
    response = make_response({'message': "cookies route"}, 200)

    return response
# response.set_cookie("current_user", "jmhw", expires=expiration_date(30), httponly=True)
@app.route('/')
def index(): 
    return '<h1>HackStacker</h1>'

@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def user_by_id(id):
        user = User.query.filter_by(id=id).first()
        if request.method == 'GET':

    
            response = make_response(
                user_schema.dump(user),
                200
            )
            return response 
    
        elif request.method == 'PATCH':
            for attr in request.get_json():
                # ipdb.set_trace()
                setattr(user, attr, request.get_json()[attr])

                db.session.add(user)
                db.session.commit()
        
                return make_response(
                    user_schema.dump(user),
                    200
                )


        elif request.method == 'DELETE':
            user = User.query.filter_by(id=id).first()
            db.session.delete(user)
            db.session.commit()

            return make_response(
                user_schema.dump(user),
                200
            )


@app.route('/users', methods =['GET', 'POST'] )
def users():
    # ipdb.set_trace()
    if request.method == 'GET':

        users = User.query.all()

        response = make_response(
            users_schema.dump(users),
            200
        )
        return response 
    
    elif request.method == 'POST':
        json_dict = request.get_json()

        user = User(
            
            username = json_dict['username'],
            bio = json_dict['bio'],
        )

        db.session.add(user)
        db.session.commit()

        response = make_response(
            user_schema.dump(user),
            201
        )


        return response

@app.route('/blog_posts', methods=['GET', 'POST'])
def blog_posts():
    if request.method == 'GET':

        blog_posts = BlogPost.query.all()

        response = make_response(
            blog_posts_schema.dump(blog_posts),
            200
        )
        return response
    
    elif request.method == 'POST':
        json_dict = request.get_json()

        blog_post = BlogPost(
            title = json_dict['title'],
            blog_content = json_dict['blog_content'],

        )

        # unknown function: now() is an issue in the migration.  
        # Always downgrade migrations prior to making changes directly to a migrations file. 
        # Add Tom Tobar to Linkedin. 
        
        db.session.add(blog_post)
        db.session.commit()

        response = make_response(
            blog_post_schema.dump(blog_post),
            201
        )

        return response



# form data object

@app.route('/blog_posts/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def blog_post_by_id(id):
    blog_post = BlogPost.query.filter_by(id=id).first()

    if request.method == 'GET':

        return make_response(
            blog_post_schema.dump(blog_post),
            200
        )

    elif request.method == 'PATCH':
        for attr in request.get_json():
            setattr(blog_post, attr, request.get_json()[attr])

            db.session.add(blog_post)
            db.session.commit()


            response = make_response(
                blog_post_schema.dump(blog_post),
                200
            )

            return response 

    elif request.method == 'DELETE': 
        db.session.delete(blog_post) 
        db.session.commit()


        response = make_response(
            blog_post_schema.dump(blog_post),
            200
        )

        return response 

@app.route('/comment/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def comment_by_id(id):
    comment = Comment.query.filter_by(id=id).first()

    if request.method == 'GET':

        return make_response(
            comment_schema.dump(comment),
            200
        )
    
    
    elif request.method == 'PATCH':
        for attr in request.get_json():
            setattr(comment, attr, request.get_json()[attr])

            db.session.add(comment)
            db.session.commit()

            # ipdb.set_trace()
            return make_response(
                comments_schema.dump(comment),
                200
            ) 
        
    elif request.method == 'DELETE':
        db.session.delete(comment)
        db.session.commit()


        response = make_response(
            comments_schema.dump(comment),
            200
        )

        return response 

@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'GET':
        comments = Comment.query.all()

        return make_response(
            comments_schema.dump(comments),
            200
        )

    elif request.method == 'POST':
        json_dict = request.get_json()
        comment = Comment(
            comment_content = json_dict['comment_content'],
        )

        db.session.add(comment)
        db.session.commit()


        return make_response(
            comments_schema.dump(comment),
            201
        )


@app.route('/categories', methods=['GET','POST'])
def categories():
    if request.method == 'GET':
        categories = Category.query.all()

        return make_response(
            categories_schema.dump(categories),
            200
        )

    elif request.method == 'POST':
        json_dict = request.get_json()
        category = Category(
            name = json_dict['name'],
            description = json_dict['description']
        )

        db.session.add(category)
        db.session.commit()

        return make_response(
            category_schema.dump(category),
            201
        )
    

@app.route('/category/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def category_by_id(id): 
    category = Category.query.filter_by(id=id).first()

    if request.method == 'GET':

        return make_response(
            category_schema.dump(category),
            200
        )
    
    elif request.method == 'PATCH':
        for attr in request.form:
            setattr(category, attr, request.get_json(attr))

            db.session.add(category)
            db.session.commit()


            return make_response(
                category_schema.dump(category),
                200
            )
        
    elif request.method == 'DELETE':
        db.session.delete(category)
        db.session.commit()


        return make_response(
            category_schema.dump(category),
            200
        )


if __name__ == '__main__':
    app.run(port=5555, debug=True)