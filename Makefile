build:
	@echo 'Building to run on Mac M1...'
	@docker build -t student_grouper:latest .

build-aws:
	@echo 'Building in deployable state for AWS Fargate...'
	@docker buildx build --platform=linux/amd64 -t student_grouper:latest .

run: 
	@echo 'Running the container...'
	@docker-compose -f docker-compose.yml up -d

kill: 
	@echo 'Bringing it down...'
	@docker-compose -f docker-compose.yml down
