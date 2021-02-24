from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from pprint import pprint
from datetime import datetime, date

## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])

    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# new_post1 = BlogPost(
#     body="Nori grape silver beet broccoli kombu beet greens fava bean potato quandong celery. Bunya nuts black-eyed "
#          "pea prairie turnip leek lentil turnip greens parsnip. Sea lettuce lettuce water chestnut eggplant winter "
#          "purslane fennel azuki bean earthnut pea sierra leone bologi leek soko chicory celtuce parsley jícama "
#          "salsify.",
#     date="August 24, 2009",
#     title="The Life of Cactus",
#     author="Angela Yu",
#     subtitle="Who knew that cacti lived such interesting lives.",
#     img_url="https =//images.unsplash.com/photo-1530482054429-cc491f61333b?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9"
#               "&auto=format&fit=crop&w=1651&q=80 "
# )
#
# new_post2 = BlogPost(
#     body="Chase ball of string eat plants, meow, and throw up because I ate plants going to catch the red dot today "
#          "going to catch the red dot today. I could pee on this if I had the energy. Chew iPad power cord steal the "
#          "warm chair right after you get up for purr for no reason leave hair everywhere, decide to want nothing to "
#          "do with my owner today.",
#     date="August 31, 2009",
#     title="Top 15 Things to do When You are Bored",
#     author="Angela Yu",
#     subtitle="Are you bored? Don't know what to do? Try these top 15 activities.",
#     img_url="https://images.unsplash.com/photo-1520350094754-f0fdcac35c1c?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9"
#               "&auto=format&fit=crop&w=1650&q=80 "
# )
#
# new_post3 = BlogPost(
#     body="Cupcake ipsum dolor. Sit amet marshmallow topping cheesecake muffin. Halvah croissant candy canes bonbon "
#          "candy. Apple pie jelly beans topping carrot cake danish tart cake cheesecake. Muffin danish chocolate "
#          "soufflé pastry icing bonbon oat cake. Powder cake jujubes oat cake. Lemon drops tootsie roll marshmallow "
#          "halvah carrot cake.",
#     date="September 5, 2009",
#     title="Introduction to Intermittent Fasting",
#     author="Angela Yu",
#     subtitle="Learn about the newest health craze.",
#     img_url="https://images.unsplash.com/photo-1543362906-acfc16c67564?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9"
#               "&auto=format&fit=crop&w=1001&q=80 "
#
# )

# db.session.add([new_post3, new_post2, new_post1])
# db.session.commit()


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/edit-post/<post_id>", methods=["POST", "GET"])
def edit_post(post_id):
    post_to_edit = BlogPost.query.get(post_id)
    post_form = CreatePostForm(obj=post_to_edit)
    if post_form.validate_on_submit():
        post_to_edit.body = request.form.get("body")
        post_to_edit.title = request.form.get("title")
        post_to_edit.author = request.form.get("author")
        post_to_edit.subtitle = request.form.get("subtitle")
        post_to_edit.img_url = request.form.get("img_url")
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))

    else:
        return render_template('make-post.html', form=post_form, title="Edit Post")


@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    blog_form = CreatePostForm()
    today = date.today().ctime()

    if blog_form.validate_on_submit():
        new_blog = BlogPost(
            body=request.form.get("body"),
            date=today,
            title=request.form.get('title'),
            author=request.form.get("author"),
            subtitle=request.form.get("subtitle"),
            img_url=request.form.get("img_url"),
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    else:
        return render_template('make-post.html', form=blog_form, title="New Post")


@app.route('/delete/<post_id>')
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run(debug=True)
