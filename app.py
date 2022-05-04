from flask import Flask, redirect, render_template,request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='this is a secret'

db=SQLAlchemy(app)
class UserForm(FlaskForm):
    name=StringField('Enter Your anme',validators=[DataRequired()])
    course=StringField('Enter Your Course',validators=[DataRequired()])
    submt=SubmitField('Go')
class Student(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    firstname=db.Column(db.String(50),nullable=False)
    # id int not null
    course=db.Column(db.String(30),nullable=False)


class Teachers(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    firstname=db.Column(db.String(50),nullable=False)

@app.route('/disp')
def display():
    qr_all=Student.query.all()
    return render_template('display.html',data=qr_all)    


@app.route('/', methods=['POST','GET'])
def home():
    stdfrm=UserForm()
    # if request.method=='POST':
    #     form=request.form
    #     addstd=Student(firstname=form['name'],course=form['course'])
    #     db.session.add(addstd)
    #     db.session.commit()
    if stdfrm.validate_on_submit():
        addstd=Student(firstname=stdfrm.name.data,course=stdfrm.course.data)
        db.session.add(addstd)
        db.session.commit()
        return redirect(url_for('display'))
    return render_template('index.html',form=stdfrm)



if __name__=='__main__':
    app.run(debug=True)