# Use the official Python image with Alpine Linux as a parent image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY  requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


# Copy the current directory contents into the container at /app
COPY . /app

# Install Redis client
RUN apk add --no-cache redis

# Run Redis server in the background
CMD ["redis-server", "--daemonize yes"]

# Define environment variable
ENV NAME World

# Run the FastAPI application
CMD ["uvicorn", "schedule_works.main:app", "--host", "0.0.0.0", "--port", "80"]
