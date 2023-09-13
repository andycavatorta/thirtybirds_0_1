class Network:
    discovery_method = "multicast"
    discovery_multicast_group = "224.3.29.71"
    discovery_multicast_port = 10020
    discovery_response_port = 10021
    discovery_caller_interval = 5
    heartbeat_interval = 5
    heartbeat_timeout_factor = 1.5
    pubsub_publish_port = 10022
	pubsub_keepalive_interval = 
	online_status_polling_interval = 
	default_network_interface = "ethernet"

class Hardware_Monitor:
    hardware_measurements_interval = 3
    nominal_range_core_temp = [15,75]
    nominal_range_core_voltage = [3.0,3.5]
    nominal_min_memory_free = 100 #MHz
    nominal_min_system_disk = 1000 #MB
    nominal_min_wifi_strength = 25


class Software_Monitor:
    update_software_on_start = False
    thirtybirds_repo_owner = "andycavatorta"
    thirtybirds_repo_name = "thirtybirds_0_1"
    thirtybirds_branch = "master"
    app_repo_owner = ""
    app_repo_name = ""
    app_branch = ""

class Reporting:
    http_port = 8000
    websocket_port = 8001
    refresh_interval = 1
    exceptions_database_name = "exceptions"
    exceptions_database_fields = {
        "id":"PRIMARY KEY",
        "ts":"INTEGER",
        "time_epoch":"INTEGER",
        "hostname":"TEXT",
        "path":"TEXT",
        "script_name":"TEXT",
        "method_name":"TEXT",
        "line_number":"INTEGER",
        "args":"TEXT",
        "exception_type":"TEXT",
        "exception_message":"TEXT",
        "forwarded":"INTEGER",#add default 0
    }
    status_database_name = "status"
    status_database_field = {
        "id":"PRIMARY KEY",
        "ts":"INTEGER",
        "time_epoch":"INTEGER",
        "hostname":"TEXT",
        "path":"TEXT",
        "script_name":"TEXT",
        "method_name":"TEXT",
        "line_number":"INTEGER",
        "args":"TEXT",
        "status_message":"TEXT",
        "forwarded":"INTEGER", #add default 0
    }
    hardware_monitor_database_name = "hardware_monitor"
    hardware_monitor_database_field = {
        "id":"PRIMARY KEY",
        "ts":"INTEGER",
        "core_temp":"FLOAT",
        "core_voltage":"FLOAT",
        "memory_free":"FLOAT",
        "system_cpu":"FLOAT",
        "system_disk":"FLOAT",
        "system_status":"TEXT",
        "system_uptime":"FLOAT",
        "wifi_strength":"FLOAT",
        "forwarded":"INTEGER",#add default 0
    }
