from initializer import Initializer
from grouper import Grouper
from plotter import Plotter

"""
This is the main runner of the grouping program. 

This is the website for plotly tables: https://plotly.com/python/table/

To Do:
    1). Add flag for only if groups of 3 and 1 person left over, make 2 groups of 2
    2). Make the student df only take students that are present (y)
    3). Finish README
"""

if __name__ == '__main__':
    
    # Get the user params and test them
    input_params = Initializer()
    input_params.print_params()
    input_params.test_params()    

    # Send params to grouper and create grouped df for plotting
    grouper = Grouper(input_params.params)
    df = grouper.group_students()
    grouper.print_student_groups(df) 

    # Run the grouping algorithm
    Plotter(input_params.params, df).plot_groups()
