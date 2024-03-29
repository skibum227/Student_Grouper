#### TODO
- Add a DB
- Add a ci/cd tool

# Student Grouper
#### Created by Skibum Woodworks Algorithm Development Division, 2021-08-09
#### (All working on AWS via Terraform 2022-06-28)

## Summary
- This repository contains the code to groups students in desired numbers, handle leftovers, and then create a 
nice visual for students.

- The code is depolyable on AWS using the terrafrom infastructure, local docker, or simly hosing the server natively. 

## Organization
	
- Main directory - contains all docker setup files and requirements

- app - core app orchestration logic and componensts

- infa - terrafromed AWS infastrucuture

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
