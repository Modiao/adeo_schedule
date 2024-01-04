
from datetime import datetime, timedelta


from schedule_works.models import Event
from schedule_works.schedule_conf import LIFE_DURATION_VALUES, SCHEDULING_CONFIGURATIONS


def get_current_time_isoformat():
    """
        This will return the current date in ISO format
    """
    current_time = datetime.now()
    current_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return current_time


def validate_time_dependency(event:Event, life_duration:str,last_execution_timestamp_job:str) -> bool:
    """
        This will check the time for the last job triggered to validate
    """

    event_timestamp = event.get('eventTimestamp')
    
    # Convert the date to iso 8601 format
    event_timestamp = to_isoformat(event_timestamp)
    current_time = to_isoformat(get_current_time_isoformat())

    # Check if current_time is greater than event_time
    if event_timestamp < current_time:
        return False

    # We check if a job is already set or not
    if not last_execution_timestamp_job:
        if event_timestamp >= current_time:
            return True
        else:
            return False
    else:
        last_execution_timestamp_job = to_isoformat(last_execution_timestamp_job)

        # Calculate expriration date based  on last_execution_timestamp_job and lifeduration
        expiration_datetime = last_execution_timestamp_job + timedelta(seconds=int(life_duration))

        # Compare input date with last_execution_timestamp_job and the expiration date 
        if last_execution_timestamp_job <= event_timestamp <= expiration_datetime:
            return True
        else:
            return False
        

def to_isoformat(date:str):
    """
        this will convert a date to Iso 8601 format
    """
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_life_duration(dependence: dict, config_name:str) -> str:
   """
       This will the life duration based on the config_name, ressource_id and dependence
   """
   ressource_id = dependence.get('resourceId')

   if ressource_id == 'cron' or ressource_id == 'BIGQUERY_TABLE_NAME_4':
       life_duration = LIFE_DURATION_VALUES.get(config_name)
   else:
        life_duration = dependence.get("lifeDuration")

   return  life_duration


RESPONSE_FORMAT = {
    'success': 'Job triggered successfully',
    'job_registered': 'Job registered',
    'failed': 'No Job triggered',
    'no_dependencies': 'No dependency validate this event'

}