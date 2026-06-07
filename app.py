from flask_sqlalchemy  import SQLAlchemy
from flask import Flask,render_template,request
import os

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOAD_FOLDER']='uploads'

db=SQLAlchemy(app)


class SchoolStudent(db.Model):
    Id=db.Column(db.Integer,primary_key=True)
    Username=db.Column(db.String(100),nullable=False)
    Class=db.Column(db.String(10),nullable=False)
    Section=db.Column(db.String(10),nullable=False)
    Roll=db.Column(db.String(20),nullable=False)
    Stream=db.Column(db.String(30),nullable=False)
    Image_path=db.Column(db.String(300),nullable=False)
   


@app.route('/calculate',methods=['POST'])
def register():
    Username=request.form['Username']
    Class=request.form['class']
    Section=request.form['section']
    Roll=request.form['Roll']
    Classroom=request.form['Classroom']
    Stream=request.form.get('type')   
    Image=request.files['image']

    filename=Image.filename
    filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
    Image.save(filepath)

    student=SchoolStudent(
        Username=Username,
        Class=Class,
        Section=Section,
        Roll=Roll,
        Stream=Stream,
        Image_path=filepath
    )
    db.session.add(student)
    db.session.commit()

   
    return render_template('register.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)



   
    

    
    