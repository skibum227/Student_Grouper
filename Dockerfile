# STEP 1: Install base image. Optimized for Python.
FROM python:3.7-slim-buster

# Step 2: Add requirements.txt file
COPY requirements.txt /requirements.txt

RUN apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        git \
        build-essential

# Step 3:  Install required python dependencies from requirements file
RUN pip install -r requirements.txt

# Step 4: Copy source code in the current directory to the container
COPY ./app /app
WORKDIR ./app

# Expose the port
EXPOSE 5050

# Lets run it!
RUN chmod +x ./gunicorn_starter.sh
ENTRYPOINT ["./gunicorn_starter.sh"]
