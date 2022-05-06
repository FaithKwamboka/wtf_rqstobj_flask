from operator import index
from flask import Flask, redirect, render_template,request, url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,FileField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_login import UserMixin,login_manager, login_required,login_user,logout_user,LoginManager,current_user

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='this is a secret'
app.config["UPLOAD_FOLDER"]='static/uploads'
bcrypt=Bcrypt(app)
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

# user form
@login_manager.user_loader
def load_user(user):
    return User.get_id(user)

class UserFrm(FlaskForm):
    name=StringField("username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submt=SubmitField('login')

#user Model
class User(db.Model,UserMixin):
    id= db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(40),nullable=False)
    password=db.Column(db.String(500),nullable=False)
#methods form UserMixin
#is_authenticated()
#is_active()
#is_anonymous()
#get_id()


@app.route('/',methods=["POST","GET"])
def login():
    frm=UserFrm()
    if frm.validate_on_submit():
        user=User.query.filter_by(username=frm.name.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,frm.password.data):
                # user.is_authenticated=True
                load_user(user)
              

                return render_template("index.html",user=current_user,form=frm)

    return render_template('index.html',form=frm)

@app.route('/dash')
@login_required
def dash():
    return f" this is the user {current_user}"
if __name__=='__main__':
    app.run(debug=True)
