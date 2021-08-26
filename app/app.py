from flask import Flask, request, render_template
from grouper import Grouper
from plotter import Plotter

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    period = request.form['period']
    groups = request.form['groups']
    #return processed_text

    params = {'period': period, 'gps':int(groups), 'distrib_lo': False, 'filename': 'student_ledger.xlsx'}
    grouper = Grouper(params)
    df = grouper.group_students()
    grouper.print_student_groups(df)
    Plotter(params, df).plot_groups()
    return "It worked!"
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
