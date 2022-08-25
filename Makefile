build:
	@echo 'Building to run on Mac M1...'
	@docker build -t student-grouper-application:latest .

build-aws:
	@echo 'Building in deployable state for AWS Fargate...'
	@docker buildx build --platform=linux/amd64 -t student-grouper-application:v3 .

run: 
	@echo 'Running the container...'
	@docker-compose -f docker-compose.yml up -d

kill: 
	@echo 'Bringing it down...'
	@docker-compose -f docker-compose.yml down
