from flask import Flask, request, render_template
from grouper import Grouper
from plotter import Plotter
import pandas as pd
#https://pythonbasics.org/flask-tutorial-templates/

# Need to get the student dict to save a dictionary output
# then it can be used to reduce the size of the dictionary that hits the grouper logic

app = Flask(__name__)
name = 'Mrs. Herr'
params_list = []

@app.route('/form')
def form(): 
    return render_template('form.html', title='Student Grouper', username=name)

@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"You are lost, got back to '/form'"
    if request.method == 'POST':
        # form_data = request.form
        # return render_template('data.html',form_data = form_data)
        period = request.form['period']
        group  = request.form['gps']
        dl     = True if request.form['gps'] == 'on' else 0

        params = {'period': period, 'gps':int(group), 'distrib_lo': dl, 'filename': 'student_ledger.xlsx'}

        params_list.append(params)
        df = pd.read_excel('student_ledger.xlsx', sheet_name=f'period_{period}')
        stu_dict = pd.Series(df.present.values,index=df.student_names).to_dict()

        return render_template('present.html', title='Student Grouper', stu_dict=stu_dict)

@app.route('/present', methods=['POST', 'GET'])
def present():
    if request.method == 'GET':
        return f"You are lost, got back to '/form'"
    if request.method == 'POST':
        print(request.form['pres'])
        grouper = Grouper(params_list[0])
        df = grouper.group_students()
        grouper.print_student_groups(df)
        Plotter(params_list[0], df).plot_groups()
        return render_template('form.html')


app.run(host='localhost', port=8000, debug=True)













