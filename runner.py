from initializer import Initializer
from grouper import Grouper
from plotter import Plotter

"""
This is the main runner of the grouping program. 

This is the website for plotly tables: https://plotly.com/python/table/

To Do:
    1). Make groups color matched
    4). Make sure requirements is complete
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
