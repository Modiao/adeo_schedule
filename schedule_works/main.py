from fastapi import FastAPI, Body, HTTPException
import os


from schedule_works.services import validate_dependencies
from schedule_works.models import Event
from schedule_works.services import connect_to_redis, logger


app = FastAPI()


@app.post("/trigger-job")
async def trigger_job(config: Event = Body(..., media_type="application/json")):
    """
    Endpoint to accept POST requests with JSON payload to trigger a job.
    """

    # We check redis connexion before doing any requests
    redis_host = os.environ.get('REDIS_HOST', 'redis')
    redis_port = os.environ.get('REDIS_PORT', 6379)

    if not connect_to_redis(host=redis_host, port=redis_port):
        raise HTTPException(status_code=400, detail=f"Please check your redis setup: host={redis_host} and port={redis_port}")

    # Log the received JSON payload
    logger.info(f"Request Received: {config}")

    # Validate scheduling configuration dependencies
    is_validated, response = validate_dependencies(event=config.model_dump(),global_config_name='SCHEDULING_CONFIGURATIONS')
    if not is_validated:
        #  raise HTTPException(status_code=400, detail=f"Dependency validation failed for eventType:{config.eventType}\
        #                     ressource_id:{config.eventResourceId} at {config.eventTimestamp}")
        raise HTTPException(status_code=400, detail=response)

    if response != "job_registered":
        # Trigger the job (replace this with your job-triggering logic)
        logger.info("Job triggered Successfully!")

    return {"message": response}


# # Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
