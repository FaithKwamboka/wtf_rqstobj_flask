
from crypt import methods
from flask import Flask, redirect, render_template,request, url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,FileField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
import os
from flask_bcrypt import Bcrypt

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='this is a secret'
app.config["UPLOAD_FOLDER"]='static/uploads'
bcrypt=Bcrypt(app)
db=SQLAlchemy(app)
migrate=Migrate(app,db)


class UserForm(FlaskForm):
    name=StringField('NAME',validators=[DataRequired()])
    course=StringField('Course',validators=[DataRequired()])
    submt=SubmitField('login')


class UploadForm(FlaskForm):
    file=FileField('Add a File',validators=[DataRequired()])
    submt=SubmitField('Upload')

class UserFrm(FlaskForm):
    name=StringField("username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submt=SubmitField('login')

class RegisterFrm(FlaskForm):
    name=StringField("username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    cnfpass=PasswordField("Confirm Password",validators=[DataRequired()])
    submt=SubmitField('login')

class FeeForm(FlaskForm):
    amount=StringField('enter Fee',validators=[DataRequired()])
    type=StringField('Enter Payment Type',validators=[DataRequired()])
    submt=SubmitField('Pay Fee')

class Student(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    firstname=db.Column(db.String(50),nullable=False)
    # id int not null
    course=db.Column(db.String(30),nullable=False)
    fee_id=db.Column(db.Integer,db.ForeignKey('fee.id'))


class Fee(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    amount=db.Column(db.Integer,nullable=False)
    type=db.Column(db.String(150),nullable=False)
    Student=db.relationship('Student',backref='Std')

class User(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(40),nullable=False)
    password=db.Column(db.String(500),nullable=False)





class Teachers(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    firstname=db.Column(db.String(50),nullable=False)

@app.route('/display', methods=["POST","GET"])
def display():
    frm=UploadForm()
    if "name" in session:
        name=session["name"]
    else:
        name=" "
    if frm.validate_on_submit():
        file=request.files["file"]
        # file2=frm.file
        file.save(os.path.join(app.config["UPLOAD_FOLDER"],file.filename))
        imgs=os.listdir(app.config["UPLOAD_FOLDER"])
        return render_template("display.html",data=imgs)
    
    return render_template('display.html',current_user=name,form=frm)    
#BCRYPT
# plain_text => {{gibberish}}
#{{Gibberish}}=>plain_text

@app.route('/register', methods=["POST","GET"])
def register():
    fr=RegisterFrm()
    if fr.validate_on_submit():
        if fr.cnfpass.data==fr.password.data:
            hash_pwd=bcrypt.generate_password_hash(fr.password.data)
        usr=User(username=fr.name.data,password=hash_pwd)
        session["name"]=fr.name.data
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('registration.html',form=fr)
@app.route("/login",methods=['POST','GET'])
def login():
    fr=UserFrm()
    if fr.validate_on_submit():
        usr=User.query.filter_by(username=fr.name.data).first()
        if usr:
            if bcrypt.check_password_hash(usr.password,fr.password.data):
                session["name"]=usr.username
        # usr=User(username=fr.name.data,password=hash_pwd)
        # db.session.add(usr)
        # db.session.commit()
                logged_in_user=session["name"]
                return redirect(url_for("home"))
    return render_template("index.html",form=fr)

@app.route('/', methods=['POST','GET'])
def home():
    stdfrm=UserForm()
    # if request.method=='POST':
    #     form=request.form
    #     addstd=Student(firstname=form['name'],course=form['course'])
    #     db.session.add(addstd)
    #     db.session.commit()
    if stdfrm.validate_on_submit():
        # addstd=Student(firstname=stdfrm.name.data,course=stdfrm.course.data)
        # db.session.add(addstd)
        # db.session.commit()
        return render_template('dashboard.html',user=session["name"])

    return render_template('dashboard.html')


@app.route('/update',methods=['POST','GET'])
def update():
    fee=FeeForm()
    if 'name' not  in session:
        return redirect(url_for('login'))

    if fee.validate_on_submit():
        paid=Fee(amount=fee.amount.data,type=fee.type.data)
        db.session.add(paid)
        db.session.commit()
    name=session["name"]

    return render_template('update.html',form=fee,current_user=name)

    
@app.route('/logout')
def logout():
    session.pop("name",None)
    return redirect(url_for('home'))
if __name__=='__main__':
    app.run(debug=True)