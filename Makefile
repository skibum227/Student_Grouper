build:
	@docker build --no-cache --tag=skibum227/student_grouper:latest .
	docker push skibum227/student_grouper:latest
