import plotly.graph_objects as go


class Plotter(object):
    def __init__(self, params, df):
        self.df = df
        self.params = params
        self.period = self.params.get('period')
        self.dont_plot = self.params.get('dont_plot')

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
                line_color='brown',
                fill_color='orange',
                align='center',
                height=45,
                font=dict(color='black', size=40)
            ),
            cells=dict(
                values=[df.student_names, df.student_group],
                align='center',
                line=dict(width=3),
                line_color='brown',
                fill_color='white',
                height=35,
                font=dict(color='black', size=30)
            ))
         ])

        fig.show()


if __name__ == '__main__':

    import pandas as pd
    params = {'period': '1', 'gps':3, 'distrib_lo': False, 'filename': 'student_ledger.xlsx', 'dont_plot': False}
    df = pd.DataFrame({'studet_names':['a', 'b', 'c'], 'student_group':[0,0,1]})
    Plotter(params, df).plot_groups()







