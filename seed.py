from faker import Faker
from models import User, BlogPost, Comment, Category
from config import db, app, bcrypt
import ipdb 
import random

fake = Faker()

print('Seeding db... 🌱')

with app.app_context():

    print("Deleting all records...❗")
    User.query.delete()
    BlogPost.query.delete()
    Comment.query.delete()
    Category.query.delete()

    usernames = []
    users = []
    
    titles = []
    blog_posts = []

    print('Creating users...👽 ')

    for i in range(20):
            username = fake.first_name()
            while username in usernames:
                  username = fake.first_name()
            usernames.append(username)

            user = User(
                  username = username,
                  bio = fake.paragraph(nb_sentences=4),
            )

            user.password_hash = user.username + 'password'
            users.append(user)

            user_id = user.id

            user.password_hash = username 
            # We are calling the password_hash setter method here


            db.session.add_all(users)
            db.session.commit()

    # BlogPost
    print("Creating blog posts...💻")

    for i in range (50):
        title = fake.sentence(nb_words=6)
        while title in titles:
            title = fake.sentence(nb_words=6)
        titles.append(title)

        blog_post = BlogPost(
            title = title,
            blog_content = fake.paragraph(nb_sentences=10),
            publication_date = fake.date_time_this_year(),
            edited_at = fake.date_time_this_year(), 
            user_id = random.choice(users).id
            # Pick and random user from the users list. 
        )
        blog_posts.append(blog_post)
        
        db.session.add_all(blog_posts)
        # Commit on every Class that has a foreign relationship. 
        db.session.commit()


            


    comment_instances = []
    comment_contents = []
    
    # Comment is returning null for comment content and user_id
    print("Creating comments...🖱️")
    for i in range (30):
        comment_content = fake.sentence(nb_words=15)
        while comment_content in comment_instances:
            comment_content = fake.sentence(nb_words=15)
        # comments.append(comment_content)
        comment_contents.append(comment_content)


        comment_instance = Comment(
            comment_content = comment_content,
            publication_date = fake.date_this_year(),
            edited_at = fake.date_this_year(),
            user_id = random.choice(users).id
        ) 

        db.session.add(comment_instance)
        comment_instances.append(comment_instance)
        # comment_instances.append(comment_instance)

    db.session.commit()



    category_names = []
    categories = []

    # Category
    print("Creating categories...🧠")

    for i in range(5):
        name = fake.word()
        while name in category_names:
            name = fake.word()
        category_names.append(name)

        category_instance = Category(
            name = name, 
            description = fake.sentence(nb_words=10), 
        )

        categories.append(category_instance)

        # Was tring to add a string to the db session with db.session.add_all(category_instance)
    
    db.session.add_all(categories)
    db.session.commit()