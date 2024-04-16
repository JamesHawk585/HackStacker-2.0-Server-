from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship, validates
from config import db, bcrypt

join_table = db.Table('blog_post_to_category',
                      db.Column("blog_post_id", db.Integer, db.ForeignKey("blog_post.id")),
                      db.Column("category_id", db.Integer, db.ForeignKey("category.id")),
                      )


class User(db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    bio = db.Column(db.String(250))

    blog_posts = db.relationship('BlogPost', backref='user')
    comments = db.relationship('Comment', backref='user')

    @validates('username')
    def validate_name(self, key, username):
        username_exists = db.session.query(User).filter(User.username==username).first()
        if not username:
            raise ValueError("username field is required")
        if username_exists:
            raise ValueError("username must be unique")
        elif key == 'username':
            if len(username) >= 80:
                raise ValueError("username must be 80 characters or less.")
        return username 

    @validates('bio')
    def validate_length(self, key, string):
        if len(string) > 250:
                raise ValueError('Bio must be 250 characters or less.')
        return string 

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}>'
    

class BlogPost(db.Model):

    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    blog_content = db.Column(db.String(5000))
    publication_date = db.Column(db.DateTime, server_default=db.func.now())
    edited_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    @validates('title', 'blog_content')
    def validate_length(self, key, string):
        if ( key == 'blog_content'):
            if len(string) >= 5000:
                raise ValueError("Blog posts must be 5000 characters or less.")
            if ( key == 'title'):
                raise ValueError('Title must be 50 characters or less.')
        return string 
    
class Comment(db.Model):

    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comment_content = db.Column(db.String(250))
    publication_date = db.Column(db.DateTime, server_default=db.func.now())
    edited_at = db.Column(db.DateTime, onupdate=db.func.now())

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    @validates('comment_content')
    def validate_length(self, key, string):
        if len(string) >= 250:
            raise ValueError('Comments must be less than 250 characters in length')
        return string

class Category(db.Model):

    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    description = db.Column(db.String(50), unique=True)

    
    @validates(name, description)
    def validate_length(self, key, string):
        if ( key == 'name'):
            if len(string) >= 30:
                raise ValueError("Category name must be 80 characters or less.")
            if ( key == 'description'):
                raise ValueError('Category description must be 250 characters or less.')
        return string 














    



