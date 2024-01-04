from functools import lru_cache
import json
import logging
import os
from typing import List
from fastapi import HTTPException
import redis

from schedule_works.models import EventType, Event, SchedulingConfiguration
from schedule_works.schedule_conf import SCHEDULING_CONFIG_NAME_CRON, SCHEDULING_CONFIG_NAME_TABLE, SCHEDULING_CONFIGURATIONS
from schedule_works.utils import RESPONSE_FORMAT, get_life_duration, validate_time_dependency 


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=None)
def connect_to_redis(host='redis', port=6379, db=0):
    """
    Connect to Redis and return the Redis client.

    Parameters:
        - host (str): Redis server hostname or IP address.
        - port (int): Redis server port.
        - db (int): Database number.

    Returns:
        redis.Redis: Redis client instance.
    """
    try:
        # Connect to Redis
        redis_client = redis.Redis(host=host, port=port, db=db)
    
        # Test the connection by trying to set and get a key
        SCHEDULING_CONFIGURATIONS_key = "SCHEDULING_CONFIGURATIONS"
        schedule_conf_data = redis_client.get(SCHEDULING_CONFIGURATIONS_key)
        if not schedule_conf_data:
            redis_client.set(SCHEDULING_CONFIGURATIONS_key,  json.dumps(SCHEDULING_CONFIGURATIONS))
        logger.info("Connected to Redis successfully")
        return redis_client
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        return None


redis_client = connect_to_redis(host=os.environ.get('REDIS_HOST', 'redis'),
                                 port=os.environ.get('REDIS_PORT', 6379))


def update_global_configurations(conf_name:str, new_configuration: dict, type:str, life_duration:str='1'):
    """
    Update the scheduling configuration
    """

    if type == 'global':
        redis_client.set(conf_name, json.dumps(new_configuration))
    else:
        redis_client.setex(conf_name, life_duration, json.dumps(new_configuration))


def check_if_config_matches(event:Event, schedule_data: SchedulingConfiguration) -> (bool, str):
    """
        This will check if the event matches with a schedule configuration
    """
    event_type = event["eventType"]
    event_ressource_id = event["eventResourceId"]

    last_execution_timestamp_job = schedule_data.get("last_execution_timestamp_job")
    config_name = schedule_data.get('name')

    # we check of each dependencies if it's valid
    for dependence in schedule_data["dependencies"]:

        life_duration = get_life_duration(dependence=dependence, config_name=config_name)

        if dependence['type'] == event_type and dependence['resourceId'] == event_ressource_id and \
             validate_time_dependency(event=event,life_duration=life_duration,\
                                      last_execution_timestamp_job=last_execution_timestamp_job):
            return True, life_duration
    return False, life_duration


def update_configuration_data(global_scheduling_configurations: List[dict], event: dict, global_config_name:str, config_name:str) -> (bool, str):
    """
        This will update the configuration on redis
    """
    event_timestamp = event.get('eventTimestamp')
    event_ressource_id = event.get('eventResourceId')
    event_type = event.get('eventType')

    if not redis_client.get(str(config_name)):
        # retreive data from redis based on the config_name if it does'nt already set
        schedule_data = SCHEDULING_CONFIGURATIONS[config_name]
        redis_client.set(config_name, json.dumps(schedule_data))

    # We convert to retreive data us a json data
    schedule_data = json.loads(redis_client.get(config_name))

    # Check validation of the event and life_duration
    is_matches, life_duration = check_if_config_matches(event=event,schedule_data=schedule_data)

    # if no dependencies validate this event
    if not is_matches:
        return (False, RESPONSE_FORMAT['no_dependencies'])

    # check if there is no workjob registered yet
    if not schedule_data.get('WorkedJobs'):
        schedule_data['WorkedJobs'] = []
        # Update last_execution_timestamp_job for the first time
        if event_type != str(EventType.TIME_BASED):
            # We update the last_execution_timestamp_job if eventType is not TIME_BASED
            schedule_data["last_execution_timestamp_job"] = event_timestamp

    # if the event is already received 
    if event_ressource_id in schedule_data.get('WorkedJobs'):
        return (False, f"Event {event_ressource_id} already registered if the last {life_duration}")
    
    # We update the data if event_type is not time_based and the life_duration is not null
    if event_ressource_id != 'cron' and event_ressource_id != 'BIGQUERY_TABLE_NAME_4':
        schedule_data["WorkedJobs"].append(event_ressource_id)
        # Update local config
        update_global_configurations(conf_name=config_name, new_configuration=schedule_data, type='local', life_duration=life_duration)

    # Update Global Configuration
    if not global_scheduling_configurations[config_name].get('Validated_event_received'):
        global_scheduling_configurations[config_name]['Validated_event_received'] = []

    # We register the global configuration to have the historical of all events
    global_scheduling_configurations[config_name]['Validated_event_received'].append(event)
    update_global_configurations(conf_name=global_config_name, new_configuration=global_scheduling_configurations, \
                        type='global')

    # schedule the job if these conditions are true
    if event_ressource_id == "BIGQUERY_TABLE_NAME_4" and 'BIGQUERY_TABLE_NAME_3' in schedule_data.get('WorkedJobs'):
        return (True, RESPONSE_FORMAT['success'])

    # Check the conditions if event_type is time_based
    if event_type == str(EventType.TIME_BASED):
        if len(schedule_data.get('WorkedJobs')) == 1 and \
            schedule_data.get('WorkedJobs')[0] == "/scheduling_configuration_1/directory/path/":
            return (True, RESPONSE_FORMAT['success'])
        elif len(schedule_data.get('WorkedJobs')) == 2: 
            return (True, RESPONSE_FORMAT['success'])
        else:
            return (False, RESPONSE_FORMAT['failed'])

    return (True, RESPONSE_FORMAT['job_registered'])


def validate_dependencies(event: Event, global_config_name:str) -> (bool, str):
    """
    Validate dependencies based on the scheduling configuration.
    """
    is_valid = False
    response = RESPONSE_FORMAT['failed']

    # get global configuration and check if it's already set in redis database
    global_scheduling_configurations = redis_client.get(global_config_name)
    if not global_scheduling_configurations:
        raise HTTPException(status_code=400, detail="No configuration's schedule is available yet")
    
    # We convert to retreive data us a json data
    global_scheduling_configurations = json.loads(global_scheduling_configurations)

    event_type  = event.get('eventType')
    
    # we handle the request based on the event_type
    if event_type == str(EventType.FILE):
        print("Calling schedule configuration: ", "SCHEDULING_CONFIGURATION_1")
        return update_configuration_data(global_scheduling_configurations=global_scheduling_configurations, 
                    event=event, global_config_name=global_config_name, config_name="SCHEDULING_CONFIGURATION_1")

    
    elif event_type == str(EventType.TIME_BASED):
        for config_name in SCHEDULING_CONFIG_NAME_CRON:
            print("Calling schedule configuration: ", config_name)
            is_valid, response = update_configuration_data(global_scheduling_configurations=global_scheduling_configurations, 
                        event=event, global_config_name=global_config_name, config_name=config_name)
            if is_valid:
                return is_valid, response
    

    elif event_type == str(EventType.TABLE):
        for config_name in SCHEDULING_CONFIG_NAME_TABLE:
            print("Calling schedule configuration: ", config_name)
            is_valid, response  = update_configuration_data(global_scheduling_configurations=global_scheduling_configurations, 
                        event=event, global_config_name=global_config_name, config_name=config_name)
            if is_valid:
                return is_valid, response
    return is_valid, response
        
    