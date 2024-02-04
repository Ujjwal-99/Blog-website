from flask import Flask, render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime

local_server="True"
with open('Config.json','r') as c:
    params=json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER= 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME =params['gmail-user'],
    MAIL_PASSWORD =params['gmail-password']
)
mail= Mail(app)
if('local server'):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

db = SQLAlchemy(app)


class Contact(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    Email = db.Column(db.String(20), nullable=False)
    Phone_no = db.Column(db.String(12), unique=True, nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    Msg = db.Column(db.String(120), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(12), unique=True, nullable=False)
    tagline = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(25),nullable=True)
@app.route("/")
def home():
    posts=Posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template('index.html',params=params,posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if "user" in session and session['user'] == params['admin_user']:
        if request.method=='POST':
            Title=request.form.get('title')
            tline=request.form.get('tline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            date=datetime.now()
            if sno==0 :
                post=Posts(title=Title ,tagline=tline,slug=slug,content=content,img_file=img_file,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title=Title
                post.tagline=tline
                post.slug=slug
                post.content=content
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)

@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if "user" in session and session['user']==params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params,posts=posts)
    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username==params['admin_user'] and userpass==params['admin_password']:
            # set the session variable
            session['user']=username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params,posts=posts  )
    else:
            return render_template("login.html", params=params)


@app.route("/contact",methods=['GET','POST'])
def contact_view() :
    if(request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')

        entry = Contact(Name=name, Email=email, Phone_no=phone, Date=datetime.now(), Msg=msg)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                           sender= email,
                           recipients = [params['gmail-user']],
                           body = msg + "/n" + phone
        )
  
    return render_template('contact.html', params=params )

@app.route("/post/<string:slug_post>", methods=['GET'])
def blog(slug_post):
    post = Posts.query.filter_by(slug=slug_post).first()
    return render_template('post.html', params=params, post=post)


app.run(debug=True)