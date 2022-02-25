build:
	@docker-compose -f docker-compose.yml up -d
#	@docker build --no-cache --tag=skibum227/student_grouper:latest .
#	docker push skibum227/student_grouper:latest
#
kill: 
	@echo 'Bringing it down...'
	@docker-compose -f docker-compose.yml down

