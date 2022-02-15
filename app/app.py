from flask import Flask, request, render_template
from grouper import Grouper
from plotter import Plotter
import pandas as pd
# https://pythonbasics.org/flask-tutorial-templates/
# https://stackoverflow.com/questions/53344797/how-create-an-array-with-checkboxes-in-flask
# make it all look nice
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/toast/

app = Flask(__name__)
name = 'Mrs. Herr'
params_list = []

@app.route('/')
@app.route('/activity_parameters')
def form(): 
    return render_template('activity_params.html', title='Student Grouper', username=name)

@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"You are lost, got back to '/activity_parameters'"

    if request.method == 'POST':
        period = request.form.get('period')
        group  = request.form.get('gps')
        dl     = True if request.form.get('dl') else False

        params = {'period': period, 'gps':int(group), 'distrib_lo': dl, 'filename': 'student_ledger.xlsx'}

        params_list.append(params)
        df = pd.read_excel('student_ledger.xlsx', sheet_name=f'period_{period}')
        stu_dict = pd.Series(df.present.values,index=df.student_names).to_dict()

        return render_template('check_attendance.html', title='Student Grouper', stu_dict=stu_dict)

@app.route('/attendance', methods=['POST', 'GET'])
def check_attendance():
    if request.method == 'GET':
        return f"You are lost, got back to '/activity_parameters'"

    if request.method == 'POST':
        present_stus=request.form.getlist('pres')
        grouper = Grouper(params_list[0], present_stus)

        df = grouper.group_students()

        grouper.print_student_groups(df)

        Plotter(params_list[0], df).plot_groups()

        return render_template('activity_params.html')

app.run(host='localhost', port=8000, debug=True)













