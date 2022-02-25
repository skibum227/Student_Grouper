import pandas as pd
import numpy as np
import argparse

class Initializer(object):

    def __init__(self):
        self.exceptions = []
        self.required_params = ['period', 'gps', 'filename']
        self.params = self._get_run_params()

    def _get_run_params(self):

        # Get the command line arguments
        inputparser = argparse.ArgumentParser(description='Input params for Student Grouper...')

        # What period to run grouper on
        inputparser.add_argument('--period', '-p', type=str, dest='period', action='store',
            #default=None, required=True, help="Select period to group")
            default='example', required=False, help="Select period to group")

        # How many groups to make
        inputparser.add_argument('--groups', '-gps', type=int, dest='gps', action='store',
            default=3, help="Select number of groups")

        # Distribute left over students
        inputparser.add_argument('--distribute_leftovers', '-dl', dest='distrib_lo', action='store_true',
            default=False, help='Flag to distribute leftover students into groups to preserve desired number')

        # Read in a different file
        inputparser.add_argument('--student_ledger_file_name', '-fn', dest='filename', action='store',
            default='student_ledger.xlsx', help='File name of the formated xlsx file containing all student names and periods')

        # Set random seed
        inputparser.add_argument('--seed', '-s', dest='seed', action='store',
            default=None, help='Set seed value for rand. num. generator so that groups dont change')

        # Do not plot
        inputparser.add_argument('--no_plot', '-np', dest='dont_plot', action='store_true',
            default=False, help='For testing, turns off plotting')

        return vars(inputparser.parse_args())

    def print_params(self):

        print('The input parameters are...')
        for k,v in self.params.items():
            print(f'    Key:{k}, Value:{v}')

    def test_params(self):

        try:
            for x in self.required_params:
                x in self.params
        except AttributeError:
            raise "Error with input parameters !!!"


if __name__ == '__main__':

    test = Initializer()
    test.print_params()
    test.test_params()




