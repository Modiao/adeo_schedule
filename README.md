# FastAPI Scheduler Project

This project is a FastAPI application with a Redis dependency, packaged using Docker Compose.

## Prerequisites

Make sure you have the following tools installed on your machine:

- [Docker](https://www.docker.com/)

## Getting Started


1. If you are using the image from docker hub (You only need to have the docker-compose.yml file) and run
    these following commands:

    ```bash
    docker pull modiao/fastapi-scheduler:1.0
    docker-compose up -d 

2. Clone the repository:

   ```bash
   git clone https://github.com/Modiao/adeo_schedule.git
   cd adeo_schedule


3. Once you have the content of the docker-compose.yml : create it in the same directory as 
   
    ```bash
    docker-compose up -d
This command will build the Docker images and start the FastAPI and Redis services.


4. If you have don't use docker and using a local redis:

    - Set up a virtual environment.
    - Install the dependencies listed in the `requirements.txt` file.
    - create a .env file and set the variables: REDIS_HOST and REDIS_PORT
    - Run:  `python schedule_works/main.py`

