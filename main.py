from flask import Flask, redirect, url_for, render_template, request, flash, send_file, session, Response
from wtforms import Form, DateField, StringField, validators
import requests
from fpdf import FPDF
from flask_sqlalchemy import SQLAlchemy
from subprocess import Popen, PIPE
import shlex
import time

HISBOTProgress = 0

#Define pdf file name
pdf_file_name = 'output.pdf'

#Init Flask
app = Flask(__name__, template_folder='./templates')

#Init database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

#Define user table in database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

#Generate report form
class FormUseToGenerateMonthlyReport(Form):
    text_field = StringField('Text Field', [validators.InputRequired(), validators.Length(min=0, max=50)])
    date_field_1 = DateField('Date Field 1', [validators.InputRequired()])
    date_field_2 = DateField('Date Field 2', [validators.InputRequired()])

#Run HISBot
def processHISBot():
    global HISBOTProgress
    print("HISBOT Running")
    session = Popen(['python3', 'HISBot.py'], stdout=PIPE, stderr=PIPE)
    while True:
        realtime_output = session.stdout.readline()

        if realtime_output.strip().decode('utf-8') == '' and session.poll() is not None:
            break

        if realtime_output:
            HISBOTProgress=realtime_output.strip().decode('utf-8')
            #if(HISBOTProgress != ""):
             #   print(int(HISBOTProgress)*10)
            if(realtime_output.strip().decode('utf-8') != ""):
                print("HISBOT process: " + realtime_output.strip().decode('utf-8') + "/10", flush=True)

#HISBot progress realtime update   
@app.route('/progress')
def progress():
	    def generate():
                global HISBOTProgress
                #print("dasd")
                #print(HISBOTProgress)
                x = 0
                while HISBOTProgress != "":
                        #print("dasdasd")
                        x = int(HISBOTProgress) * 10
                        #print(x)
                        yield "data:" + str(x) + "\n\n"
                        time.sleep(0.5)

	    return Response(generate(), mimetype= 'text/event-stream')

#Create homepage route
@app.route("/", methods=['GET', 'POST'])
#Callback function
def report():
    if session.get('logged_in'):
        form = FormUseToGenerateMonthlyReport()
        if request.method == 'POST':
            #run HISBOT
            processHISBot()
            #Generate monthly report pdf file
            generate_pdf_file(request.form["text_field"], request.form["date_field_1"], request.form["date_field_2"])
            #flash('Thanks for registering')
            #Send monthly report pdf file to client. Client will download this file.
            #TODO: allow download file
            #send_file(pdf_file_name, mimetype='application/force-download')
            return send_file(pdf_file_name, mimetype='application/pdf')
        return render_template('generatemonthlyreportpage.html', form=form, progress = HISBOTProgress)
    else:
        return render_template('index.html', message="Hello!")
    
#Register route
@app.route('/register/', methods=['GET', 'POST'])
#Callback function
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')

#Login route
@app.route('/login/', methods=['GET', 'POST'])
#Callback function
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('report'))
        return render_template('index.html', message="Incorrect Details")

#Logout route
@app.route('/logout', methods=['GET', 'POST'])
#Callback function
def logout():
    session['logged_in'] = False
    return redirect(url_for('report'))

#Generate pdf file. PS: Code cua thay viet vao day
def generate_pdf_file(text, date_1, date_2):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, text + "##############" + date_1 + "##############" + date_2)
    pdf.output(pdf_file_name, 'F')
    
#Main
app.secret_key = "ThisIsNotASecret:p"
db.create_all()
