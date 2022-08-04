import pandas as pd
import numpy as np


class Grouper(object):
    def __init__(self, params, present_stus=None):

        self.params = params
        self.period = f'period_{self.params.get("period")}'
        self.gps = params.get('gps')
        self.seed = int(params.get('seed')) if params.get('seed') else np.random.randint(0, 10000000)

        # This parameter if true will add leftover students to other groups
        #   to preserve the desired groups. If false will make smaller group.
        self.distrib_lo = params.get('distrib_lo')
        self.filename = params.get('filename')

        self.student_df = params.get('student_df') 
        self.group_deliniator = len(self.student_df) // self.gps

    def _read_in_ledger(self, present_stus=None):

        df = pd.read_excel(self.filename, sheet_name=self.period)

        # if there are students who are not present
        if present_stus:
            print(present_stus)
            df['present'] = np.where(df.student_names.isin(present_stus), 'y', 'n')
            
        # Only count students that are present
        df = df[df.present.eq('y')]

        if df.empty:
            raise "File name incorrect, file is missing, or no student is present"
        else:
            return df

    def _dont_distribute_leftovers(self, df):

        for x in range(len(df) % self.gps, 0, -1):
                df.iloc[-x, df.columns.get_loc('student_group')] = self.group_deliniator

        return df

    def group_students(self):

        # Copy it
        df = self.student_df.copy()

        # Assigning Random number between 0 and 1
        np.random.seed(self.seed)
        df['num'] = [np.random.random() for x in range(len(df))]

        # Sort by the random value
        df = df.sort_values('num').reset_index(drop=True)

        # Assign the group
        df['student_group'] = df.index % self.group_deliniator

        # Directs stragglers to there own, smaller group, with requested specific for groups of 3
        # This directs how the grouping should occur...
        # - if distributing leftover students is desired then the the next if statement is skipped
        #     b/c that already happens
        # - if distribution is not desired, the function runs to create another group for the leftovers
        # - if the grouping is 3 and there is one student left over, automatically make 2 groups of 2 (requested)

        print(f'{self.distrib_lo}, yeahhhh')
        if not self.distrib_lo:
            print(' !!! Left over Students have NOT been distributed ...')
            df = self._dont_distribute_leftovers(df)

        if self.gps == 3 and len(df) % self.gps == 1 and not self.distrib_lo:
            print(' !!! One person left over in groups of 3, making 2 groups of 2 ...')
            df.iloc[0,3] = self.group_deliniator
        else:
            print(' !!! Left over Students have been distributed ...')

        if not self.distrib_lo:
            df = self._dont_distribute_leftovers(df)

        # Increment student groups by 1 b/c there is no board "0" in Alex's class
        df.student_group += 1

        return df

    def print_student_groups(self, df):

        for x in range(self.group_deliniator if self.distrib_lo else self.group_deliniator + 1):
            temp = df.loc[df.student_group.eq(x)]['student_names'].to_list()
            print(f'Group Number {x} ...')
            for y in temp:
                print(f'   {y}')
            print('')
