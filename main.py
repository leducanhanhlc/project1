from flask import Flask, redirect, url_for, render_template, request, flash, send_file
from flask_simplelogin import SimpleLogin
from flask_simplelogin import login_required
from wtforms import Form, DateField, StringField, validators
import requests
from fpdf import FPDF

pdf_file_name = 'output.pdf'

#Init Flask
app = Flask(__name__, template_folder='./')

#Setting config
app.config['SECRET_KEY'] = 'something-secret'
app.config['SIMPLELOGIN_USERNAME'] = 'admin'
app.config['SIMPLELOGIN_PASSWORD'] = 'admin'

#Init simple login
SimpleLogin(app)

class FormUseToGenerateMonthlyReport(Form):
    text_field = StringField('Text Field', [validators.InputRequired(), validators.Length(min=0, max=50)])
    date_field_1 = DateField('Date Field 1', [validators.InputRequired()])
    date_field_2 = DateField('Date Field 2', [validators.InputRequired()])

#Create homepage route
@app.route("/", methods=['GET', 'POST'])

#Force user login to access homepage
@login_required

#Content of homepage
def report():
    form = FormUseToGenerateMonthlyReport()
    print("POST LÊLELELádas")
    if request.method == 'POST':
        #Generate monthly report pdf file
        generate_pdf_file(request.form["text_field"], request.form["date_field_1"], request.form["date_field_2"])
        #flash('Thanks for registering')
        #Send monthly report pdf file to client. Client will download this file.
        return send_file(pdf_file_name, mimetype='application/force-download')
    return render_template('generatemonthlyreportpage.html', form=form)

#Generate pdf file. PS: Code cua thay viet vao day
def generate_pdf_file(text, date_1, date_2):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, text + "##############" + date_1 + "##############" + date_2)
    pdf.output(pdf_file_name, 'F')
    
