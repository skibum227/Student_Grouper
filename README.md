# Student Grouper
### Created by Skibum Woodworks Algorithm Development Division, 2021-08-09
#### (All working on AWS 2022-02-27)

## Summary
- This repository contains the code to groups students in desired numbers, handle leftovers, and then create a 
nice visual for students.

- The code is set up so that the grouper logic can be ran locally as well as in a container. Additionally this container can be pushed up to AWS and ran on ECS (the smallest provisioning can be used which costs approximately $0.15 a day). 

## Organization
	
- Main directory - contains all docker setup files and requirements

- gunicorn_starter.sh - core starting scipt to bring up app with WSGI

- app/app.py - core app orchestration logic

- app/templates/* - contains all of the html templates

- app/runner.py - command line usage (for developement only)

- app/initializer.py - works with commandline interface and only used in developement

- app/grouper.py - contains the logic for creating the student groups

- app/plotter.py - takes the output from the grouper and makes a nice visualization of the groups with plotly

- app/student_ledger.xlsx - manually updated list of students in each class so they can be accessed (will become a db at some point)

## How to Use

-  Enter students names into `student_ledger.xlsx` for each period and demarcate if they are present or not. See the **period_example** sheet in the excel file for an example of the inputs (the letters are stand-ins for student names)

### Local deployment
1. Run the starter script: `./app/gunicorn_starter.sh`

1. Go to 0.0.0.0:5000 in browser

### Local container deployment (runs with gunicorn)

1. Build the docker file: `make build` (use `make rebuild` if there is a change)

1. Go to 0.0.0.0:5000 in browser

### AWS deployment

Note: [These steps are used to get running on AWS](https://towardsdatascience.com/deploy-your-python-app-with-aws-fargate-tutorial-7a48535da586)

1. Update the **VERSION** file with the release version and tag the commit

1. Build the docker file: `make build` (use `make rebuild` if there is a change)

1. Push the image up to AWS ECR

1. Bring down the current task

1. Update the ECS task definition to use the new image

1. Start a new ECS task with Fargate (use first security group)

1. Update the inbound rules to accept port **5000** at 0.0.0.0 (click on the ENI from the task page)
