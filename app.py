from flask_sqlalchemy  import SQLAlchemy
from flask import Flask,render_template,request
import face_recognition as fr
import os
import base64
from io import BytesIO
from PIL import Image
import numpy as np

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:TVN%402026@localhost:5432/attendance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOAD_FOLDER']='uploads'

db=SQLAlchemy(app)
known_encodings=[]
known_students=[]

class CollegeStudent(db.Model):
  
    Id=db.Column(db.Integer,primary_key=True)
    Username=db.Column(db.String(100),nullable=False)
    Class=db.Column(db.String(10),nullable=False)
    Section=db.Column(db.String(10),nullable=False)
    Roll=db.Column(db.String(20),nullable=False)
    Stream=db.Column(db.String(30),nullable=False)
    Image_path=db.Column(db.String(300),nullable=False)
   
class Attendance(db.Model):
    Id=db.Column(db.Integer,primary_key=True)
    Status=db.Column(db.String(30),nullable=False)
    Time=db.Column(db.DateTime, default=db.func.current_timestamp())
    student_id=db.Column(db.Integer,db.ForeignKey('college_student.id'))

    student=db.relationship('CollegeStudent', backref='attendances')


@app.route('/calculate',methods=['POST'])
def register():
    Username=request.form['Username']
    Class=request.form['class']
    Section=request.form['section']
    Roll=request.form['Roll']
   
    Stream=request.form.get('type')   
    Image=request.files['image']

    filename=Image.filename
    filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
    Image.save(filepath)

    student=CollegeStudent(
        Username=Username,
        Class=Class,
        Section=Section,
        Roll=Roll,
        Stream=Stream,
        Image_path=filepath
    )
    db.session.add(student)
    db.session.commit()

   
    return render_template('register2.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

def preload_students():
    students=CollegeStudent.query.all()
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
      return render_template("attendance.html",
        Message="⚠️ No face detected. Try again")
    unknown_encoding = encodings[0]

    matches=fr.compare_faces(known_encodings,unknown_encoding)
    distances = fr.face_distance(known_encodings, unknown_encoding)

    if True in matches:
        idx=matches.index(True)
        student=known_students[idx]
        similarity = (1 - distances[idx]) * 100
        similarity = round(similarity, 2)  # e.g., 87.45%
        attendance = Attendance(
        Status="Present",
        student_id=student.Id
        )
        db.session.add(attendance)
        db.session.commit()
        
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


import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

at_dept = pd.DataFrame({
    'Dept': ['CSE','ECE','MNC','ME','EE','CHE','CE','MME','BT'],
    'at': [172,65,48,172,63,57,64,55,34],
    'total': [187,68,60,187,79,72,75,60,55]
})
at_dept['Attendance %'] = round((at_dept['at'] / at_dept['total']) * 100, 2)

at_sect = pd.DataFrame({
    'Sect': ['A','B','C','D','E','F','G','H'],
    'at': [102,87,76,100,95,83,97,89],
    'total': [121,123,122,123,118,120,119,121]
})
at_sect['Attendance %'] = round((at_sect['at'] / at_sect['total']) * 100, 2)

at_day = pd.DataFrame({
    'Day': ['Mon','Tue','Wed','Thu','Fri'],
    'Attendance %': [87,82,76,79,84]
})

at_month = pd.DataFrame({
    "Month": ['Jan','Feb','Mar','Apr'],
    "Attendance %": [76, 85, 82, 89]
})

at_college = pd.DataFrame({
    'Attendance': ['Above 75%','Above 50%','Below 50%'],
    'No. of Students': [3412,512,120]
})


 # Month-wise bar
fig_month = px.bar(at_month, x='Month', y='Attendance %')
fig_month.update_layout(
    hovermode="closest",
    xaxis_title="Month",
    yaxis_title="Avg. Attendance %",
    bargap=0.5,
    bargroupgap=0.1
)
fig_month.update_layout(
    paper_bgcolor="#cbf9f9",   
         
)
fig_month.update_traces(marker_color="#00eaff")

 # Department bar
fig = px.bar(at_dept, x='Dept', y='Attendance %')
fig.update_layout(
    hovermode="closest",
    xaxis_title="Department",
    yaxis_title="Avg. Attendance%",
    yaxis=dict(range=[0,100]),
    bargap=0.5,
    bargroupgap=0.1
 )
fig.update_layout(
    paper_bgcolor="#cbf9f9",   
        
 )
fig.update_traces(marker_color="#da1a32")

# Section bar
fig1 = px.bar(at_sect, x='Sect', y='Attendance %')
fig1.update_layout(
    hovermode="closest",
    xaxis_title="Section (1st Year Classes)",
    yaxis_title="Avg. Attendance %",
    yaxis=dict(range=[0,100]),
    bargap=0.5,
    bargroupgap=0.1
 )
fig1.update_traces(marker_color="#0897f6")
fig1.update_layout(
    paper_bgcolor="#cbf9f9",   
        
 )
# College pie
fig2 = px.pie(at_college, names='Attendance', values='No. of Students', hole=0.3, color='Attendance')
fig2.update_layout(
    paper_bgcolor="#cbf9f9",   
        
)
 # Day-wise line
fig_day = go.Figure()
fig_day.add_trace(go.Scatter(
    x=at_day["Day"],
    y=at_day["Attendance %"],
    mode="lines+markers",
    line=dict(color="blue", width=3),
    fill="tozeroy",
    fillcolor="rgba(0,255,0,0.2)",
    name="Day-wise Attendance"
 ))
fig_day.update_layout(
    yaxis=dict(range=[70,90]),
    hovermode="closest"
)

fig_day.update_layout(
    paper_bgcolor="#cbf9f9",   
        
)

fig.update_layout(
    title=dict(text="Department Attendance", font=dict(size=20, color="#da1a32"), x=0.5, xanchor="center")
)

fig1.update_layout(
    title=dict(text="Section Attendance", font=dict(size=20, color="#0897f6"), x=0.5, xanchor="center")
)

fig_month.update_layout(
    title=dict(text="Monthly Attendance", font=dict(size=20, color="#00eaff"), x=0.5, xanchor="center")
)

fig2.update_layout(
    title=dict(text="College Attendance Distribution", font=dict(size=20, color="#333333"), x=0.5, xanchor="center")
)

fig_day.update_layout(
    title=dict(text="Day-wise Attendance Trend", font=dict(size=20, color="blue"), x=0.5, xanchor="center")
)
 # --- Summary metrics ---
total_students = at_college['No. of Students'].sum()
avg_attendance = round(at_dept['Attendance %'].mean(), 2)
best_dept = at_dept.loc[at_dept['Attendance %'].idxmax(), 'Dept']
below_75 = at_college.loc[at_college['Attendance'] == 'Above 50%', 'No. of Students'].values[0] \
           + at_college.loc[at_college['Attendance'] == 'Below 50%', 'No. of Students'].values[0]

 # --- Create summary figure ---
summary_fig = go.Figure()

summary_fig.add_annotation(
    text=f"<b>Total Students:</b> {total_students}",
    x=0.5, y=1, xref="paper", yref="paper",  
    xanchor="center", yanchor="top",          
    showarrow=False,
    font=dict(size=18, color="blue",family="Trebuchet MS")
 )
summary_fig.add_annotation(
    text=f"<b>Average Attendance:</b> {avg_attendance}%",
    x=0.5, y=0.8, xref="paper", yref="paper",
    xanchor="center", yanchor="top",
    showarrow=False,
    font=dict(size=18, color="blue",family="Trebuchet MS")
 )
summary_fig.add_annotation(
    text=f"<b>Best Attendance in Dept:</b> {best_dept}",
    x=0.5, y=0.6, xref="paper", yref="paper",
    xanchor="center", yanchor="top",
    showarrow=False,
    font=dict(size=18, color="blue",family="Trebuchet MS")
 )
summary_fig.add_annotation(
    text=f"<b>Below 75%:</b> {below_75} students",
    x=0.5, y=0.4, xref="paper", yref="paper",
    xanchor="center", yanchor="top",
    showarrow=False,
    font=dict(size=18, color="blue",family="Trebuchet MS")
 )

summary_fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    paper_bgcolor="#cbf9f9",
    plot_bgcolor="#cbf9f9",
    margin=dict(l=20, r=20, t=40, b=20),  
 )





dash_app = dash.Dash(__name__,
                     server=app,
                     url_base_pathname='/dashboard')

dash_app.layout = html.Div([
    html.H1("Attendance Dashboard",
    
    style={
        "textAlign": "center",          
        "color": "#004466",             
        "fontFamily": "Trebuchet MS",  
        "fontSize": "36px",            
        "fontWeight": "bold",          
        "marginBottom": "20px"          
    }),
       
    html.Div([
        dcc.Graph(figure=fig1, style={"width":"35%", "display":"inline-block","border":"10px solid #4ce1e1"}),
        dcc.Graph(figure=fig, style={"width":"35%", "display":"inline-block","border":"10px solid #4ce1e1"}),
        dcc.Graph(figure=fig_month, style={"width":"22%", "display":"inline-block","border":"10px solid #4ce1e1"}),
        dcc.Graph(figure=fig2, style={"width":"30%", "display":"inline-block","border":"10px solid #4ce1e1"}),
        dcc.Graph(figure=fig_day, style={"width":"30%", "display":"inline-block","border":"10px solid #4ce1e1"}),
        dcc.Graph(figure=summary_fig, style={"width":"30%", "display":"inline-block", "border":"10px solid #4ce1e1"}
 )

    ]),
   
 ],
 style={
    "background": "#4ce1e1",
    "padding": "20px"
 })





if __name__ == "__main__":
  
    with app.app_context():
        db.create_all()
        preload_students()
    app.run(debug=True)
