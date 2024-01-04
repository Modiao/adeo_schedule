
from enum import Enum
from typing import List
from pydantic import validator, BaseModel, ConfigDict
from datetime import datetime


class EventType(Enum):
    """  
        This class will help us to enum the type
    """
    FILE = "FILE"
    TIME_BASED = "TIME_BASED"
    TABLE = "TABLE"

    def __str__(self) -> str:
        return "%s" % self.value


class Event(BaseModel):
    """  
        This class will help us to use the enaum and build the request
    """
    eventType: EventType
    eventResourceId: str
    eventTimestamp: str

    # The use_enum_values=True parameter, in this case, 
    # would mean that enums used within the configuration will have their actual values 
    model_config = ConfigDict(use_enum_values=True)

    @validator("eventTimestamp")
    def validate_iso8601_timestamp(cls, value):
        try:
            # Attempt to parse the value as an ISO 8601 timestamp
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            raise ValueError("Invalid ISO 8601 timestamp format : %Y-%m-%dT%H:%M:%S.%fZ")
        return value

class Dependence(BaseModel):
    """  
        This class will help us to use the enum and build the request
    """
    type: EventType
    resourceId: str
    lifeDuration: str

    # The use_enum_values=True parameter, in this case, 
    # would mean that enums used within the configuration will have their actual values 
    model_config = ConfigDict(use_enum_values=True)

class SchedulingConfiguration(BaseModel):
    name: str
    dependencies: List[Dependence]