from signal import valid_signals
from flask import Flask, flash, redirect, render_template,request, url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,FileField,TextAreaField,EmailField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_login import UserMixin,login_manager, login_required,login_user,logout_user,LoginManager,current_user
import os
import io
from flask_mail import Message, Mail
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

import app2
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='this is a secret'
app.config["UPLOAD_FOLDER"]="static/uploads"
app.config["MAIL_DEFAULT_SENDER"]="Steveotieno701@gmail.com"
app.config["MAIL_USERNAME"]="Steveotieno701@gmail.com"
app.config["MAIL_PORT"]=465
app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_USE_TLS"]=False
app.config["MAIL_USE_SSL"]=True
app.config["MAIL_PASSWORD"]=app2.pass_w
mail=Mail(app)

bcrypt=Bcrypt(app)
db=SQLAlchemy(app)
migrate=Migrate(app,db)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view='login'

# user form
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class UserFrm(FlaskForm):
    name=StringField("username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submt=SubmitField('login')

class RegisterFrm(FlaskForm):
    name=StringField("username",validators=[DataRequired()])
    email=EmailField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    cnfpass=PasswordField("Confirm Password",validators=[DataRequired()])
    submt=SubmitField('Register') 

class UploadForm(FlaskForm):
    file=FileField('Add a File',validators=[DataRequired()])
    submt=SubmitField('Upload')

class PostForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()],render_kw={'placeholder':'Title'})
    post=TextAreaField("Post",render_kw={"placeholder":"Type Post..."})
    submt=SubmitField("Submit Post")

# posting Post
# post form
# users are going to post
#---comments

#user Model
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(40),nullable=False)
    email=db.Column(db.String(40),nullable=False)
    password=db.Column(db.String(40),nullable=False)
    postman=db.relationship('Post',backref="postman")


class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    post=db.Column(db.String(700),nullable=False)
    poster=db.Column(db.Integer,db.ForeignKey('user.id'))

class Images(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    uploader_id=db.Column(db.Integer,db.ForeignKey('user.id'))

@app.before_first_request
def create_tables():
    db.create_all()
#methods form UserMixin
#is_authenticated()
#is_active()
#is_anonymous()
#get_id()
    # def get_(self):
    #     return (self.id)
    # ../../../images.jpg
  

@app.route('/',methods=["POST","GET"])
def login():
    frm=UserFrm()
    if request.method=="POST":
        if frm.validate_on_submit():
            user=User.query.filter_by(username=frm.name.data).first()
            if user:
                if bcrypt.check_password_hash(user.password,frm.password.data):
                    #load_user(user)
                    login_user(user)
                    return redirect(url_for('dashboard'))
    return render_template('index.html',form=frm)

@app.route('/register',methods=['POST','GET'])
def register():
    frm=RegisterFrm()
    if frm.validate_on_submit():
        if frm.password.data==frm.cnfpass.data:
            hash_pwd=bcrypt.generate_password_hash(frm.password.data)
            newuser=User(username=frm.name.data,email=frm.email.data,password=hash_pwd)
            db.session.add(newuser)
            db.session.commit()
            # msg=Message(subject=" POSTER APP REGISTRATION",recipients=[frm.email.data],body=frm.name.data+" Thank you for registering")
            # mail.send(msg)
            return redirect(url_for('login'))
        else:
            flash(" Passwords do not match")

      

    return render_template('register.html',form=frm)

@app.route("/uploadimage",methods=["POST","GET"])
@login_required
def uploadimage():
    user=current_user
    frm=UploadForm()
    if frm.validate_on_submit():
        file=request.files["file"]
        file.save(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(file.filename)))
        upload=Images(name=secure_filename(file.filename),uploader_id=user.id)
        db.session.add(upload)
        db.session.commit()
        return redirect(url_for("viewimage"))
    return render_template("imageupload.html",form=frm,user=user.username)

@app.route("/viewallimages",methods=["POST","GET"])
@login_required
def viewallimages():
    allimages=Images.query.all()
    return render_template("viewall.html",images=allimages)

@app.route("/viewimage",methods=["POST","GET"])
@login_required
def viewimage():
    userimages=Images.query.filter_by(uploader_id=current_user.id).all()
    return render_template("imageview.html",name=current_user.username,images=userimages)

    
@app.route('/dashboard',methods=["POST","GET"])
@login_required
def dashboard():
    frm=PostForm()
    posts=Post.query.all()
    if frm.validate_on_submit():
        new_post=Post(title=frm.title.data,post=frm.post.data,poster=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        frm.title.data=""
        frm.post.data=""

    return render_template('dashboard.html',user=current_user.username,form=frm,posts=posts)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__=='__main__':
    app.run(debug=True)
