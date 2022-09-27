# TODO
- Add scheduling to infa code
	- in console
	- https://peterwadid1.medium.com/start-stop-ecs-fargate-tasks-using-lambda-cloudwatch-events-rules-b453aad4e1f6
	- https://towardsaws.com/start-stop-aws-ecs-services-on-a-schedule-b35e14d8d2d5
- Add a DB
- Add a ci/cd tool

# Student Grouper
### Created by Skibum Woodworks Algorithm Development Division, 2021-08-09
#### (All working on AWS via Terraform 2022-06-28)

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

- infa/* - Terraformed AWS resources and modules to automatically host and run the app

## How to Use

-  Enter students names into `student_ledger.xlsx` for each period and demarcate if they are present or not. See the **period_example** sheet in the excel file for an example of the inputs (the letters are stand-ins for student names)

### Local deployment
1. Run the starter script: `./app/gunicorn_starter.sh`

1. Go to 0.0.0.0:5050 in browser

### Local container deployment (runs with gunicorn)

1. Build the docker file: `make build`

1. Bring up the app image: `make run`

1. Go to 0.0.0.0:5050 in browser

### AWS deployment

Note: [The imaged needs to be rebuilt due to the Mac M1's archetecutre](https://stackoverflow.com/questions/67361936/exec-user-process-caused-exec-format-error-in-aws-fargate-service)

1. Create a release commit and tag with the new version number

	- Update the **VERSION** file with the release version

	- Update the CHANGELOG.md with new features

1. Build the docker file: `make build-aws`

1. Push the image up to AWS ECR via commands in ECR (pass AWS env vars: `AWS_PROFILE=personal`)

1. The image will get picked up and brought up automatically

1. Check the AWS ALB to find the DNS host name in order to access the app 
