import pytest
from datetime import datetime, timedelta
from schedule_works.utils import get_current_time_isoformat, validate_time_dependency, to_isoformat, get_life_duration

# Mocking the 'Event' class for testing purposes
class MockEvent:
    def __init__(self, event_timestamp):
        self.event_timestamp = event_timestamp

    def get(self, key):
        return getattr(self, key, None)

# Example test cases
def test_get_current_time_isoformat():
    result = get_current_time_isoformat()
    assert result is not None

def test_to_isoformat():
    input_date = "2023-01-04T12:00:00.000Z"
    result = to_isoformat(input_date)
    assert isinstance(result, datetime)

def test_get_life_duration():
    dependence = {"resourceId": "cron"}
    config_name = "SCHEDULING_CONFIGURATION_1"
    result = get_life_duration(dependence, config_name)
    assert result is not None
    assert result == "3600"


if __name__ == "__main__":
    pytest.main()
