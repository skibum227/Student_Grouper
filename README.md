# Student Grouper
### Created by Skibum Woodworks Algorithm Development Division, 2021-08-09
All working 2022-02-24

https://towardsdatascience.com/deploy-your-python-app-with-aws-fargate-tutorial-7a48535da586

## Summary
This repository contains the code to groups students in desired numbers, handle leftovers, and then create a 
nice visual for students.

## How to Use
The `app` directory contains the core logic to run the grouping

1). Enter students names into `student_ledger.xlsx` for each period and demarcate if they are present or not. See the **period_example** sheet in the excel file for an example of the inputs (the letters are stand-ins for student names)

2). `runner.py` is the main program for creating the groupings. Designating the period (adding a `--period` or `-p` in the command line) is required and will fail if not added. The program also defaults to making groups of 3. Typing `python runner.py --help` will print possible syntax uses to screen.

3). Once ran, the output table will come up in the defaulted browser. Each group will be demarcated and color coded. Colors and the student allocations are randomized. Student allocations can be reproduced by designating a seed value in the command line (`--seed` or `-s`)

4). run docker-compose up to bring up the app in a container
