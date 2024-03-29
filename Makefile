build:
	@echo 'Building to run on Mac M1...'
	@docker build -t student-grouper-application:latest .

build-aws:
	@echo 'Building in deployable state for AWS Fargate...'
	@docker buildx build --platform=linux/amd64 -t student-grouper-application:v3 .

run: 
	@echo 'Running the container...'
	@docker-compose -f docker-compose.yml up -d
	@AWS_PROFILE=personal python ./testing/initialize_db.py

kill: 
	@echo 'Bringing it down...'
	@docker-compose -f docker-compose.yml down
