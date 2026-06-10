from flask_sqlalchemy  import SQLAlchemy
from flask import Flask,render_template,request
import face_recognition as fr
import os
import base64
from io import BytesIO
from PIL import Image
import numpy as np

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOAD_FOLDER']='uploads'

db=SQLAlchemy(app)
known_encodings=[]
known_students=[]

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

def preload_students():
    students=SchoolStudent.query.all()
    for student in students:
        if os.path.exists(student.Image_path):
            img=fr.load_image_file(student.Image_path)
            encodings=fr.face_encodings(img)
        if encodings:
            known_encodings.append(encodings[0])
            known_students.append(student)

@app.route('/recognize',methods=['POST'])

def recognize():
    data=request.get_json()
    image_data=data['image']
    img_bytes=base64.b64decode(image_data.split(",")[1])   
    img=Image.open(BytesIO(img_bytes))
    img_array=np.array(img)
    encodings=fr.face_encodings(img_array)

    if not encodings:
        unknown_encoding=encodings[0]
    matches=fr.compare_faces(known_encodings,unknown_encoding)
    distances = fr.face_distance(known_encodings, unknown_encoding)

    if True in matches:
        idx=matches.index(True)
        student=known_students[idx]
        similarity = (1 - distances[idx]) * 100
        similarity = round(similarity, 2)  # e.g., 87.45%
        
        return render_template("attendance.html",
        Message="✅ Attendance Marked",
        Name=student.Username,
        Roll=student.Roll,
        Class=student.Class,
        Section=student.Section,
        percentage=similarity
        )
    else:
        return render_template("attendance.html",
        Message="⚠️ Face not recognized. Try again ")

   
    

    
    
