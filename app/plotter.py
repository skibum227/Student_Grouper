import plotly.graph_objects as go
import plotly
import seaborn as sns
import random
import dash
import dash_core_components as dcc
import dash_html_components as html
import json

# Pastel color list, randomized with white in front
color_list = sns.color_palette("pastel", as_cmap=True)
random.shuffle(sns.color_palette("pastel", as_cmap=True))
color_list = ['white'] + color_list

"""
This class builds a color palette out of 11 colors then plots the table
However, this function randomizes the color order, but white is always first
    then repeats the pattern for the desired number of groups
"""

class Plotter(object):
    def __init__(self, params, df):
        self.df = self._add_color_column(df)
        self.params = params
        self.period = self.params.get('period')
        self.dont_plot = self.params.get('dont_plot')

    def _build_expanded_color_palette(self, max_groups):

        # First get full dups of list
        dup_color_list = []
        for x in range(max_groups // len(color_list)):
            print(x)
            dup_color_list.append(color_list)
        dup_color_list = [val for sublist in dup_color_list for val in sublist]

        # Now get the left overs from the list
        lo_color_list = max_groups % len(color_list)

        # Concat and return
        return dup_color_list + color_list[0:lo_color_list]

    def _add_color_column(self, df):

        # Total required colors
        num_colors = df.student_group.max() + 1

        # Build list
        exp_color_list = self._build_expanded_color_palette(num_colors)

        # Create the mapping
        color_map = {x: exp_color_list[x] for x in range(num_colors)}

        # Run the mapping
        df['color'] = df['student_group'].map(color_map)
        return df

    def plot_groups(self):
        if self.dont_plot:
            print('Plotting turned off ...')
            return

        df = self.df.sort_values('student_group').reset_index(drop=True)

        fig = go.Figure(
            data=[go.Table(
            header=dict(
                values=['Student Name', f'Period {self.period} Groups'],
                line=dict(width=3),
                line_color='black',
                fill_color='white',
                align='center',
                height=45,
                font=dict(color='black', size=40)
            ),
            cells=dict(
                values=[df.student_names, df.student_group],
                align='center',
                line=dict(width=3),
                line_color='black',
                fill_color=[df.color],
                height=40,
                font=dict(color='black', size=30)
            ))
         ])
        fig.update_layout(width=2000, height=2000)

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON
        # fig.show()


if __name__ == '__main__':

    import pandas as pd
    params = {'period': '1', 'gps':3, 'distrib_lo': False, 'filename': 'student_ledger.xlsx', 'dont_plot': False}
    df = pd.DataFrame({'student_names':['a', 'b', 'c'], 'student_group':[0,0,1]})
    Plotter(params, df).plot_groups()







