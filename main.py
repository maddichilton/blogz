from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:LaunchCode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'y337kGcys&zP3B'

# TO DO: in Blogz assignment: add dynamic user pages
# ELSE: errors in login/signup???

def validity(e, p, pv):
    p_error_msg = ""
    pv_error_msg = ""
    e_error_msg = ""

    if " " in p or len(p) < 3 or len(p) > 20:
        p_error_msg = "Invalid password"
    if p != pv:
        pv_error_msg += "Passwords must match"
    if e != "":
        ats = 0
        dots = 0
        for i in e:
            if i == "@":
                ats += 1
            if i == ".":
                dots += 1
            else:
                continue
        if ats != 1 or dots != 1:
            e_error_msg = "Invalid email"
        if " " in e or len(e) < 3 or len(e) > 20:
            e_error_msg = "Invalid email"
    if p == "":
        p_error_msg = "Field cannot be blank"
    if pv == "":
        pv_error_msg = "Field cannot be blank"
    if e == "":
        e_error_msg = "Field cannot be blank"
    
    if p_error_msg == "" and pv_error_msg == "" and e_error_msg == "":
        allvalid = True
    else:
        allvalid = False

    return e_error_msg, p_error_msg, pv_error_msg, allvalid



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(75))
    body = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    blogs_length = int(len(blogs))
    recent_id = blogs_length - 1
    if not recent_id < 0:
        recent_blog = blogs[recent_id]
    else:
        recent_blog = ""
    
    users = User.query.all()
    
    return render_template('index.html',title="build a blog!", 
        blogs=blogs, recent_blog=recent_blog, users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    blog_body = ""
    blog_title = ""
    error = ""

    current_user = User.query.filter_by(email=session["user"]).first()

    if request.method == 'POST':
        blog_body = request.form['body']
        blog_title = request.form['title']
        if blog_body == "" or blog_title == "":
            error = "error! field cannot be blank!"
            blogs = Blog.query.all()
            if blog_body == "":
                body_error = error
            else:
                body_error = ""
            if blog_title == "":
                title_error = error
            else:
                title_error = ""
            return render_template('newpost.html',title="build a blog!", blogs=blogs, 
        body_error=body_error, title_error=title_error, old_title=blog_title, old_body=blog_body)
        new_blog = Blog(blog_title, blog_body, current_user)
        db.session.add(new_blog)
        db.session.commit()

        blogs = Blog.query.all()
        blogs_length = len(blogs)
        new_guy = blogs[blogs_length - 1]
        blog_id = new_guy.id

        return redirect('/blog?id={0}'.format(blog_id))

    blogs = Blog.query.all()

    return render_template('newpost.html',title="build a blog!", 
        blogs=blogs, error=error, old_title=blog_title, old_body=blog_body)

@app.route('/blog', methods=['GET'])
def blog_posts():
    blogs = Blog.query.all()

    if request.args.get('id'):
        blog_id = int(request.args.get('id')) - 1
        blogs = Blog.query.all()
        blog = blogs[blog_id]
        return render_template("post.html", blog=blog) 

    return render_template('blog.html',title="build a blog!", 
        blogs=blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user.password == password:
            session['user'] = user.email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        signup_attempt = validity(email, password, verify)

        e_error = signup_attempt[0]
        pw_error = signup_attempt[1]
        pv_error = signup_attempt[2]

        if signup_attempt[3] == False:
            if e_error != "":
                flash(e_error)
            if pw_error != "":
                flash(pw_error)
            if pv_error != "":
                flash(pv_error)
            return redirect ("/signup")

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.email
            return redirect('/')
        else:
            flash('User already exists', 'error')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog_posts']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')


if __name__ == '__main__':
    app.run()