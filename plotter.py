import plotly.graph_objects as go

# https://plotly.com/python/table/

class Plotter(object):
    def __init__(self, df, params)
        self.df = df
        self.params = params
        self.period = f'Period {self.params.get("period")}'

    def plot_groups(self):
        df = self.df.sort_values('student_group').reset_index(drop=True)
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Student Name', 'Group'],
                line=dict(width=3),
                line_color='brown',
                fill_color='orange',
                align='center',
                height=40,
                font=dict(color='black', size=20)
            ),
            cells=dict(
                values=[df.name, df.student_group],
                align='left',
                line=dict(width=3),
                line_color='brown',
                fill_color='white',
                height=30,
                font=dict(color='black', size=16)
            ))
         ])

        fig.show()

if __name__ == '__main__':

    import pandas as pd
    # fake df
