from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:LaunchCode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(75))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_body = request.form['body']
        blog_title = request.form['title']
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()
    blogs_length = int(len(blogs))
    recent_id = blogs_length - 1
    recent_blog = blogs[recent_id]
    
    return render_template('index.html',title="build a blog!", 
        blogs=blogs, recent_blog=recent_blog)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    blog_body = ""
    blog_title = ""
    error = ""

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
        new_blog = Blog(blog_title, blog_body)
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


if __name__ == '__main__':
    app.run()