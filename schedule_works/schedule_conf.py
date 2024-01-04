SCHEDULING_CONFIGURATIONS = {
    "SCHEDULING_CONFIGURATION_1": {
        "name": "SCHEDULING_CONFIGURATION_1",
        "dependencies": [
            {"type": "TIME_BASED", "resourceId": "cron", "lifeDuration": "0"},
            {"type": "FILE", "resourceId": "/scheduling_configuration_1/directory/path/", "lifeDuration": "3600"},
        ],
    },
    "SCHEDULING_CONFIGURATION_2": {
        "name": "SCHEDULING_CONFIGURATION_2",
        "dependencies": [
            {"type": "TIME_BASED", "resourceId": "cron", "lifeDuration": "0"},
            {"type": "TABLE", "resourceId": "BIGQUERY_TABLE_NAME_1", "lifeDuration": "86400"},
            {"type": "TABLE", "resourceId": "BIGQUERY_TABLE_NAME_2", "lifeDuration": "86400"},
        ],
    },
    "SCHEDULING_CONFIGURATION_3": {
        "name": "SCHEDULING_CONFIGURATION_3",
        "dependencies": [
            {"type": "TABLE", "resourceId": "BIGQUERY_TABLE_NAME_3", "lifeDuration": "86400"},
            {"type": "TABLE", "resourceId": "BIGQUERY_TABLE_NAME_4", "lifeDuration": "0"},
        ],
    },
}

SCHEDULING_CONFIG_NAME_CRON = ['SCHEDULING_CONFIGURATION_1', "SCHEDULING_CONFIGURATION_2"]

SCHEDULING_CONFIG_NAME_TABLE = ['SCHEDULING_CONFIGURATION_2', "SCHEDULING_CONFIGURATION_3"]

LIFE_DURATION_VALUES =  {
                                'SCHEDULING_CONFIGURATION_1': "3600", 
                                'SCHEDULING_CONFIGURATION_2': "86400",
                                'SCHEDULING_CONFIGURATION_3': "86400"
                    }


