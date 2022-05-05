
from flask import Flask, redirect, render_template,request, url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='this is a secret'

db=SQLAlchemy(app)
migrate=Migrate(app,db)
class UserForm(FlaskForm):
    name=StringField('NAME',validators=[DataRequired()])
    course=StringField('Course',validators=[DataRequired()])
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





class Teachers(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    firstname=db.Column(db.String(50),nullable=False)

@app.route('/disp')
def display():
    qr_all=Student.query.all()
    if session["name"]!=None:
        name=session["name"]
    else:
        name="no user logged in"
    
    return render_template('display.html',current_user=name)    


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
        session["name"]=stdfrm.name.data
        return redirect(url_for('display'))

    return render_template('index.html',form=stdfrm)


@app.route('/update',methods=['POST','GET'])
def update():
    fee=FeeForm()
    
    if fee.validate_on_submit():
        paid=Fee(amount=fee.amount.data,type=fee.type.data)
        db.session.add(paid)
        db.session.commit()
    if session["name"]!=None:
        name=session["name"]
    else:
        name="no user logged in"

    return render_template('update.html',form=fee,current_user=name)
@app.route('/logout')
def logout():
    session["name"]=None
    return redirect(url_for('home'))
if __name__=='__main__':
    app.run(debug=True)