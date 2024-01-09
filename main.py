'''
<<< From Local to Remote >>>

1) Environmental Variables
    - import os, import dotenv import load_dotenv, load dotenv()
    - create .env in terminal
    - key in all the secret variables in .env

2) Gitignore
    - create .gitignore
    - go to gitignore.io website and key in "Flask"
    - copy all text and paste into .gitignore
    - Ensure these files are included :  .env , .DS_Store

3) Git
    - git init (initialise a Git)
    - git add <file> or git add .
    - git commit -m "message"
    - git status
    - git log
    - git checkout <id> <- temporarily move back to commit
    - git revert <id> <- revert by creating new commit
        eg. git revert C2 --> C3, C4, remains same, C5 created but undo anything from C2
    - git reset <id>  <- undo the commit by deleting commit
        eg. git reset C2 --> restore to C2, and delete C3, C4, etc.


4) Remote GitHub
    - click on VCS on menu bar
    - Enable Version Control
    - when pop up screen - make sure you choose 'Git'
    - Go to VCS or GitHub , and click on "+" to "Log in via GitHub"
    - *  new GitHub repo by going to VCS -> Import into Version Control -> Share Project on GitHub
            Repository name : anything
            Remote : origin <-- do not change
            Description : anything
    - * existng GitHub repo , just click "push"

5) gunicorn
    - pip install gunicorn
    - manually add "Gunicorn==21.2.0" into requirements.txt

6) PostgreSQL
    - pip install psycopg2-binary
    - manually add "Psycopg2-binary==2.9.9" into requirements.txt
    - modify 2 parts of main.py :
        a) ##CONNECT TO DB <<<< For sqlite only >>>>>
        b) ## <<<<< Creating DB on Sqlite >>>>>>>



'''
from flask import Flask, render_template, redirect, url_for, flash, abort,request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_wtf import CSRFProtect
from functools import wraps
import hashlib
import smtplib
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import date
post_date= date.today().strftime("%d %B %Y")

# IMPT : To use bootstrap5 - do not install flask-bootstrap - install Bootstrap-Flask

# Access variables ===============
my_email = os.getenv("my_email")
password = os.getenv("password")
secret_key = os.getenv("secret_key")
#===================================

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
bootstrap = Bootstrap5(app)
csrf=CSRFProtect(app)
ckeditor = CKEditor(app)

##CONNECT TO DB <<<< For sqlite only >>>>>
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

##CONNECT TO DB <<<< For both sqlite and postresql use >>>>>
# Check if DATABASE_URL environment variable is set (indicating PostgreSQL)

if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://", 1)
else:
    # Default to SQLite if DATABASE_URL is not set
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
'''
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
'''
############################

## LOGIN-MANGAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = "Please log-in first. Thank you !"
login_manager.login_view = 'login' # In order for the above msg to work
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))   # get id from session,then retrieve user object from database

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if not current_user.is_authenticated or current_user.id not in [1, 2]:
            return abort(403)
        # otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function
# Note : Also need to change in Indext.html and Post.html ({%if current_user.id in [1, 2]%})

#============================================

##CONFIGURE TABLES
## IMPT : Inside the database (blog.db), there are three tables - Blogposts,User and Comment.
'''IMPT : As of July 2022, backref is considered legacy and back_populates is preferred.'''

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(250))
    name = db.Column(db.String(100))

    # Establishing User(Parent/One) - BlogPost(Child/Many)
    b_posts = db.relationship("BlogPost", back_populates="author", lazy=True)
    ## Below is the old method - backref
    ## b_posts = db.relationship('BlogPost', backref='author', lazy=True)

    # Establishing the User(Parent/One) - Comment(Child/Many)
    comments = relationship("Comment", back_populates="comment_author", lazy=True)

    # NOTE : One of the above use "db.relationship" , and the other does not :
    ''' In summary, whether to use relationship or db.relationship depends on how
        you've imported the function. If you've imported it directly from sqlalchemy.orm,
        you can use relationship without the db prefix. If you've imported it using from
        flask_sqlalchemy import SQLAlchemy, then you should use db.relationship to 
        access it through the Flask-SQLAlchemy extension'''


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    #author = db.Column(db.String(250), nullable=False) ## IMPT - This has been replaced using the relationship link with User
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Establishing the BlogPost(Child/Many) - User(Parent/One)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id")) #<- must use the table name eg. "users"
    author = db.relationship("User", back_populates="b_posts")
    ## ## Below is the old method - backref
    ##author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Establishing the BlogPost(Parent/One) - Comment(Child/Many)
    comments = relationship("Comment", back_populates="parent_post", cascade="all, delete-orphan", passive_deletes=True, lazy=True)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)

    # Establishing the Comment(Child/Many) - User(Parent/One)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # Must use the table name, e.g., "users"
    comment_author = relationship("User", back_populates="comments")

    # Establishing the Comment(Child/Many) - BlogPost(Parent/One)
    post_id = db.Column(db.Integer,
                        db.ForeignKey("blog_posts.id", ondelete="CASCADE", deferrable=True, initially="DEFERRED"),
                        nullable=False)
    parent_post = relationship("BlogPost", back_populates="comments")


'''
    # Establishing the Comment(Child/Many) - User(Parent/One)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id")) #<- must use the table name eg. "users"
    comment_author = relationship("User", back_populates="comments")

    # Establishing the Comment(Child/Many) - BlogPost(Parent/One)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False)
    parent_post = relationship("BlogPost", back_populates="comments")

'''



## <<<<< Creating DB on Sqlite >>>>>>>
## Line below only required once, when creating DB.
# with app.app_context():
#     db.create_all()

## <<<<<< Creating DB on both Sqlite and Postresql >>>>>>>
# Create tables if running in a local environment

# if 'DATABASE_URL' not in os.environ:
#     with app.app_context():
#         db.create_all()

#####################################################
# To replace "from flask_gravatar import Gravatar "
# For more details and options , see https://docs.gravatar.com/general/images/
def gravatar_url(email, size=150, rating='g', default='identicon', force_default=False):
    hash_value = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_value}?s={size}&d={default}&r={rating}&f={force_default}"

app.jinja_env.filters['gravatar'] = gravatar_url
######################################################


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route('/author/<int:author_id>')
def get_posts_by_author(author_id):
    print(f"Received Author ID: {author_id}")
    # Assuming you have a User model and a BlogPost model
    user = User.query.get(author_id)
    if user:
        posts = user.blog_posts  # Access the lazy-loaded blog posts
        return render_template("index.html", all_posts=posts, current_user=current_user, author=user)
    else:
        # Handle the case when the user with the specified ID is not found
        return render_template("author_not_found.html")


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data
        name = form.name.data

        ### Check user email already exist ###
        if User.query.filter_by(email=email).first():
            # User already exists
            flash("You've already signed up with that email. Log-in instead.")
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=email,
            password=hashed_password,
            name=name
        )
        db.session.add(new_user)
        db.session.commit()

        # Log in and authenticate user after adding details to database
        login_user(new_user)

        return redirect(url_for('get_all_posts'))
    return render_template("register.html",form=form,current_user=current_user)


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        # User not exist
        if not user:
            # User not exist
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))

        # User exist
        # password not exist
        elif not check_password_hash(user.password,password ):
            flash("Password incorrect, please try again.")
            return redirect(url_for('login'))

        # User exist
        # Password exist
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html",form=form,current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>",methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)

    if form.validate_on_submit():
        ## Note this part is made redundant as we have make the textbox disappear in the post.html
        # if not current_user.is_authenticated:
        #     flash("You need to login or register to comment.")
        #     return redirect(url_for('login'))

        new_comment = Comment(
            text = form.comment_text.data,
            # author_id = current_user.id,
            # post_id = post_id,
            comment_author=current_user,
            parent_post=requested_post,
            date = post_date
        )
        print(f"Comment_author:{current_user} Parent_post:{requested_post}")
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post',post_id=requested_post.id))

    return render_template("post.html", post=requested_post, form=form, current_user=current_user)


@app.route("/new-post",methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=post_date,
            body=form.body.data,
            author_id=current_user.id, # we are capturing author_id now
            img_url=form.img_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>",methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        #author_id=current_user.id, # # Change to whoever is editing
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        #post.author_id = current_user.id # # Change to whoever is editing
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form,current_user=current_user,is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    # comment_to_delete = Comment.query.get(post_id)
    # db.session.delete(comment_to_delete)
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route('/delete_comment/<int:comment_id>', methods=['GET','POST'])
@login_required  # Ensure only authenticated users can delete comments
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    # Check if the current user is an admin or the comment owner
    if current_user.id in [1, 2] or current_user.id == comment.comment_author.id:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully!', 'success')
    else:
        flash('You do not have permission to delete this comment.', 'danger')
    return redirect(url_for('show_post', post_id=comment.post_id))


@app.route("/about")
def about():
    return render_template("about.html",current_user=current_user)


@csrf.exempt
@app.route("/contact", methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]
        print(f"Name:{name} Email: {email} Phone: {phone} Message: {message}")
        send_email(name,email,phone,message)
        return render_template('contact.html', msg_sent=True)
    else:
        return render_template("contact.html", msg_sent=False)

def send_email(name,email,phone,message):
    message = f"Subject : New Message\n\nName : {name}\nEmail: {email}\nPhone: {phone}\n Message: {message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, to_addrs=my_email,
                            msg= message
                            )

#When you run the script directly (python main.py),
# it starts the Flask development server. When deployed on Render with Gunicorn,
# the if __name__ == "__main__": block is ignored, and Gunicorn is used to serve the application.
if __name__ == "__main__":
    app.run(debug=True)
    # app.debug = True
    # app.run(host='0.0.0.0', port=5000)

