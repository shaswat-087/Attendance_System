from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy import create_engine
from flask import Flask,render_template,request,redirect,url_for,session,jsonify
import os
from sqlalchemy import cast, Date
import random
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime,timedelta

app=Flask(__name__)
CORS(app)

app.secret_key='your key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:TVN%402026@localhost:5432/attendance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOAD_FOLDER']='uploads'

db=SQLAlchemy(app)
global known_encodings,known_students
known_encodings=[]
known_students=[]


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/student")
def student():
    return render_template('student.html')

@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')



class Institute(db.Model):
    ID=db.Column(db.Integer,primary_key=True,nullable=False)
    Name=db.Column(db.String(100),nullable=False)
    password=db.Column(db.Text,nullable=False)

class CollegeStudent(db.Model):
  
    Id=db.Column(db.Integer,primary_key=True)
    Username=db.Column(db.String(100),nullable=False)
    Class=db.Column(db.String(10),nullable=False)
    Section=db.Column(db.String(10),nullable=False)
    password=db.Column(db.String(200),nullable=False)
    Roll=db.Column(db.String(20),nullable=False)
    Stream=db.Column(db.String(30),nullable=False)
    College=db.Column(db.String(100),nullable=False)
    Image_path=db.Column(db.String(300),nullable=False)
   
class Attendance(db.Model):
    Id=db.Column(db.Integer,primary_key=True)
    Status=db.Column(db.String(30),nullable=False)
    Time=db.Column(db.DateTime, default=db.func.current_timestamp())
    student_id=db.Column(db.Integer,db.ForeignKey('college_student.Id'))
    student=db.relationship('CollegeStudent', backref='attendances')

@app.route("/adminregister",methods=['GET','POST'])
def adminregister():
    if request.method=='POST':
      password=request.form['password']
      Name=request.form['Name']
      existing_admin = Institute.query.filter_by(Name=Name).first()
      if existing_admin:
          Message="Admin with this name already exists. Please choose another."
          return render_template('adminregister.html',
                                 Message=Message)
      hashed_password = generate_password_hash(password)

      admin=Institute(
          Name=Name,
          password=hashed_password,

       )
      db.session.add(admin)
      db.session.commit()
      return redirect(url_for('adminlogin'))

    else:
     return render_template('adminregister.html')

@app.route("/adminlogin",methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST':
     Name=request.form['Name']
     password=request.form['password']
    
     admin=Institute.query.filter_by(Name=Name).first()

     if admin and check_password_hash(admin.password,password):
        #Valid Password
        session['admin_id']=admin.ID
        return redirect(url_for('admindash'))
     else:
        return "Invalid Username or Password",401
    
    else:
    
     return render_template('adminlogin.html')





@app.route("/admindash")
def admindash():
    from datetime import datetime
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 6, 22, 23, 59, 59)
    
    Stream = request.args.get("Stream")
    Section = request.args.get("Section")
    
    query = CollegeStudent.query
    
    if Stream and Stream != 'All':
        query = query.filter_by(Stream=Stream)
    if Section and Section != 'All':
        query = query.filter_by(Section=Section)
        
    students = query.order_by(CollegeStudent.Roll.asc()).all()
    
    report = []
    
    for student in students:
        records = Attendance.query.filter(
            Attendance.student_id == student.Id,
            Attendance.Time >= start_date,
            Attendance.Time <= end_date
        ).all()
      
        total = len(records)
        present = sum(1 for r in records if r.Status == "Present")
        percentage = (present / total) * 100 if total > 0 else 0
   
        report.append({
            "Id": student.Id,
            "Username": student.Username,
            "Roll": student.Roll,
            "Stream": student.Stream,
            "Section": student.Section,
            "percentage": round(percentage, 2)
        })

    return render_template('admindash.html', report=report)

    

@app.route('/calculate',methods=['GET','POST'])
def register():
   if request.method=='POST': 
    Username=request.form['Username']
    Class=request.form['class']
    Section=request.form['section']
    Roll=request.form['Roll']
    password=request.form['password']
    Stream=request.form['Stream']  
    College=request.form['College']
    Image=request.files['image']

    hashed_password = generate_password_hash(password)
   
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Save file
    filename = Image.filename
    filepath = os.path.join(upload_folder, filename)
    Image.save(filepath)

    student=CollegeStudent(
        Username=Username,
        Class=Class,
        Section=Section,
        Roll=Roll,
        Stream=Stream,
        College=College,
        password=hashed_password,
        Image_path=filepath
    )
    db.session.add(student)
    db.session.commit()
    return redirect(url_for('student'))

   else:
    return render_template('register2.html')



@app.route('/login',methods=['GET','POST'])
def login():
  if request.method == 'POST':
    Username=request.form['Username']
    Roll=request.form['Roll']
    password=request.form['password']
    
    student=CollegeStudent.query.filter_by(Username=Username,Roll=Roll).first()

    if student and check_password_hash(student.password,password):
        #Valid Password
        session['student_id']=student.Id
        return redirect(url_for('analytics'))
    else:
        return "Invalid Username or Password",401
    
    
  return render_template('login.html')




import face_recognition as fr
import os
import base64
from io import BytesIO
from PIL import Image
import numpy as np

def preload_students():
    students=CollegeStudent.query.all()
    for student in students:
        if os.path.exists(student.Image_path):
            img=fr.load_image_file(student.Image_path)
            encodings=fr.face_encodings(img)
            if encodings:
              known_encodings.append(encodings[0])
              known_students.append(student)

@app.route('/recognize',methods=['GET','POST'])
def recognize():
    now=datetime.now()
    
    class_start = now.replace(hour=12, minute=0, second=0, microsecond=0)
    deadline = class_start + timedelta(minutes=15)
    #Using this logic if  class start time is 9 am, entry after 9:15 am is marked as late

    if request.method=='POST':
        data=request.get_json()
        image_data=data.get('image')
        img_bytes=base64.b64decode(image_data.split(",")[1])   
        
        img=Image.open(BytesIO(img_bytes)).convert('RGB')
        img_array=np.array(img)
        encodings=fr.face_encodings(img_array)

        if not encodings:
            return jsonify({"message":"⚠️ No face detected. Try again"})
            
        unknown_encoding = encodings[0]

        matches=fr.compare_faces(known_encodings,unknown_encoding)
        distances = fr.face_distance(known_encodings, unknown_encoding)

        if True in matches:
            idx=matches.index(True)
            student=known_students[idx]
            similarity = (1 - distances[idx]) * 100
            similarity = round(similarity, 2)  
           
            if now>deadline:
             return jsonify({
                   "name": student.Username,
                    "roll": student.Roll,
                    "class": student.Class,
                    "section": student.Section,
                    "percentage": similarity,
            
                    "Message": " ⚠️ Attendance marked as Late. Entry beyond 10 minutes of start time."
             })

       

         
            attendance = Attendance(
                Status="Present",
                student_id=student.Id
            )
            now = datetime.now()
            today = now.date()

            existing = db.session.query(Attendance).filter(
             Attendance.student_id == student.Id,   # Matches the student's unique ID
            cast(Attendance.Time, Date) == today   # Strips the hours/minutes to compare just the date
            ).first() 
            if existing:
                return jsonify({ "name": student.Username,
                    "roll": student.Roll,
                    "class": student.Class,
                    "section": student.Section,
                    "percentage": similarity,
                   "message": "Attendance already marked for Today."
                   })
            db.session.add(attendance)
            db.session.commit()
            
            return jsonify({
                    "message": "✅ Attendance Marked",
                    "name": student.Username,
                    "roll": student.Roll,
                    "class": student.Class,
                    "section": student.Section,
                    "percentage": similarity
            })
        else:
            return jsonify({"message": "⚠️ Face not recognized. Try again"})
    else:
        return render_template("attendance.html")

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
                     url_base_pathname='/dashboard/')

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
        dcc.Graph(figure=summary_fig, style={"width":"30%", "display":"inline-block", "border":"10px solid #4ce1e1"})

    ]),
   
 ],
 style={
    "background": "#4ce1e1",
    "padding": "20px"
 })

@app.route("/dashboard")
def dashboard():
    return redirect("/dashboard/")
import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
import numpy as np
from flask import session, has_request_context, render_template, redirect

dash_app2 = dash.Dash(__name__, server=app, url_base_pathname='/personal_dashboard/')

def serve_analytics_layout():
    if not has_request_context():
        return html.Div("Loading Dashboard...")

    if 'student_id' not in session:
        return html.Div([
            html.H2("Unauthorized Access"),
            html.A("Please go back and login", href="/login")
        ])

    student_id = session['student_id']

    total = Attendance.query.filter_by(student_id=student_id).count()
    
    if total > 0:
        present = Attendance.query.filter_by(student_id=student_id, Status="Present").count()
        my_percentage = (present / total) * 100
        absent = 100 - my_percentage
    else:
        present = 0
        my_percentage = 0
        absent = 100

    students = CollegeStudent.query.all()
    class_attendance = []

    for student in students:
        total_classes = Attendance.query.filter_by(student_id=student.Id).count()
        present_classes = Attendance.query.filter_by(student_id=student.Id, Status="Present").count()
        if total_classes > 0:
            percentage = (present_classes / total_classes) * 100
            class_attendance.append(percentage)

    if not class_attendance:
        class_attendance = [0]

    fig5 = px.pie(values=[my_percentage, absent], names=["Present", "Absent"], hole=0.5, color_discrete_sequence=["#24D27E", "#6A6969"])
    fig5.update_layout(
        title=dict(text="Your Attendance in Class", font=dict(size=20, color="#0897f6"), x=0.5, xanchor="center"),
        paper_bgcolor="#cbf9f9",
    )

    mean = np.mean(class_attendance)
    std = np.std(class_attendance)
    
    if std == 0:
        std = 0.001 

    x = np.linspace(0, 100, 200)
    pdf = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
    percentile = norm.cdf(my_percentage, mean, std) * 100
    percentile = round(percentile, 2)

    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(
        x=x, y=pdf, mode="lines", line=dict(color="blue", width=3), name="Class Distribution"
    ))

    fig_curve.add_trace(go.Scatter(
        x=[my_percentage, my_percentage], y=[0, max(pdf)], mode="lines", line=dict(color="red", dash="dash"), name="My Attendance"
    ))

    fig_curve.add_trace(go.Scatter(
        x=x[x <= my_percentage], y=pdf[x <= my_percentage], mode="lines", line=dict(color="green", width=0), fill="tozeroy", fillcolor="rgba(0,0,236,0.2)", name="Percentile Area"
    ))

    fig_curve.update_layout(
        title={
            "text": "Probability Curve<br><sup>You are ahead of " f"{percentile}% of students in terms of attendance</sup>",
            "x": 0.5, 
            "xanchor": "center",
            "font": dict(size=20, color="#004466")
        },
        xaxis_title="Attendance %",
        yaxis_title="Probability Density",
        paper_bgcolor="#cbf9f9",
        plot_bgcolor="#ffffff",
        hovermode=False
    )

    return html.Div([
        html.H1("Personal Analytics", style={
            "textAlign": "center", "color": "#004466", "fontFamily": "Trebuchet MS", 
            "fontSize": "36px", "fontWeight": "bold", "marginBottom": "20px"
        }),
        html.Div([
            dcc.Graph(figure=fig5, style={"width":"40%", "display":"inline-block", "border":"20px solid #4ce1e1", "marginLeft":"100px"}),
            dcc.Graph(figure=fig_curve, style={"width":"40%", "display":"inline-block", "border":"20px solid #4ce1e1", "marginRight":"10px"})
        ])
    ], style={"background": "#76f8f8", "padding": "20px", "minHeight": "100vh"})


dash_app2.layout = serve_analytics_layout

@app.route('/analytics')
def analytics():
    if 'student_id' not in session:
        return render_template('returnmsg.html')
   
    return redirect('/personal_dashboard/')

if __name__ == "__main__":
    with app.app_context():
     
        db.create_all()
        preload_students()
    app.run(debug=True)
