#!/usr/bin/python

"""
to do: 
    network.discovery - limit accepted responses to hostnames listest in settings
    network.duplex_sockets - limit accepted responses to hostnames listest in settings
    network.pub_sub - add encodings for json, streaming, base64, etc.



"""

import inspect
import netifaces
import os
import queue
import settings as tb_settings
import socket
import sys
import threading
import time
import traceback


#############################
##### C O N S T A N T S #####
#############################

class topics:
    ACTIVATE_STATUS_CAPTURE_TYPE = "__activate_status_capture_type__"
    APP_GIT_STATUS = "__app_git_status__"
    APP_GIT_TIMESTAMP = "__app_git_timestamp__"
    APP_SCRIPTS_STATUS = "__app_scripts_status__"
    APP_SCRIPTS_VERSION = "__app_scripts_version__"
    CORE_TEMP = "__core_temp__"
    CORE_VOLTAGE = "__core_voltage__"
    DEACTIVATE_STATUS_CAPTURE_TYPE = "__deactivate_status_capture_type__"
    DEADMAN = "__deadman__"
    ERROR = "__error__"
    EXCEPTION = "__exception__"
    HEARTBEAT = "__heartbeat__"
    HARDWARE_MONITOR = "__hardware_monitor__"
    MEMORY_FREE = "__memory_free__"
    OS_UPTIME = "__os_uptime__"
    OS_VERSION = "__os_version__"
    PULL_APP_FROM_GITHUB = "__pull_app_from_github__"
    PULL_THIRTYBIRDS_FROM_GITHUB = "__pull_thirtybirds_from_github__"
    REBOOT = "__reboot__"
    RESTART = "__restart__"
    RUN_APP_UPDATE_SCRIPTS = "__run_app_update_scripts__"
    RUN_THIRTYBIRDS_UPDATE_SCRIPTS = "__run_thirtybirds_update_scripts__"
    SCRIPT_RUNTIME = "__script_runtime__"
    SHUTDOWN = "__shutdown__"
    STATUS = "__status__"
    SYSTEM_CPU = "__system_cpu__"
    SYSTEM_DISK = "__system_disk__"
    SYSTEM_UPTIME = "__system_uptime__"
    THIRTYBIRDS_GIT_STATUS = "__thirtybirds_git_status__"
    THIRTYBIRDS_GIT_TIMESTAMP = "__thirtybirds_git_timestamp__"
    THIRTYBIRDS_SCRIPTS_STATUS = "__thirtybirds_scripts_status__"
    THIRTYBIRDS_SCRIPTS_VERSION = "__thirtybirds_scripts_version__"
    WIFI_STRENGTH = "__wifi_strength__"

class verbs:
    PUSH = "PUSH"
    REQUEST = "REQUEST"
    RESPOND = "RESPOND"
    COMMAND = "COMMAND"
    SET = "SET"

class network_discovery_roles:
    DISCOVERY_ROLE_RESPONDER = "DISCOVERY_ROLE_RESPONDER"
    DISCOVERY_ROLE_CALLER = "DISCOVERY_ROLE_CALLER"


##############################
##### R E P O R T I N G  #####
##############################

class Reporting_Logging(threading.Thread):
    def __init__(
        self,
        database_table_name,
        database_field_names,
        status_callback,
        exception_callback
        )
        self.database_table_name = database_table_name
        self.database_field_names = database_field_names
        self.ensure_table_exists()

    def ensure_table_exists(self):
        # 
        pass

    def insert(self, names_and_values):
        pass

    def delete(self, sql_clauses_t):
        pass

    def select(self, sql_clauses_t):
        pass

    def select_all_not_forwarded(self, epoch_time):
        pass

class Reporting(threading.Thread):
    """
    systems:
        logging
        forwarding (including catching up with log when network becomes available)
        printing to stdout

    This class handles five types of data:
        exceptions
        status messages
        hardware monitor messages


    Because this system records exceptions, it must start recording before other systems are initialized.
    So this system starts in a state with limited functionality.
    Its full functionality starts after it receives the signal tht all systems are initialized.

    """
    def __init__(
            hostname,
            http_port,
            websocket_port,
            refresh_interval,
            logfile_path,
            exceptions_database_name,
            exceptions_database_fields,
            status_database_name,
            status_database_field,
            hardware_monitor_database_name,
            hardware_monitor_database_field,
            print_exceptions_to_stdout,
            host_is_controller,
            add_to_upstream_message_queue,
        ):
        threading.Thread.__init__(self)
        self.message_queue = queue.Queue()
        self.all_systems_initialized = False 

        self.hostname = hostname
        self.http_port = http_port
        self.websocket_port = websocket_port
        self.refresh_interval = refresh_interval
        self.logfile_path = logfile_path
        self.add_to_upstream_message_queue = add_to_upstream_message_queue
        self.exceptions_database_name = exceptions_database_name
        self.exceptions_database_fields = exceptions_database_fields
        self.status_database_name = status_database_name
        self.status_database_field = status_database_field
        self.hardware_monitor_database_name = hardware_monitor_database_name
        self.hardware_monitor_database_field = hardware_monitor_database_field
        self.host_is_controller = host_is_controller
        self.print_exceptions_to_stdout = print_exceptions_to_stdout

        self.ensure_database_exists()

        self.exception_logging = Reporting_Logging(
            settings.exceptions_database_name,
            settings.exceptions_database_fields,
            status_callback,
            exception_callback
        )

        self.status_logging = Reporting_Logging(
            settings.status_database_name,
            settings.status_database_fields,
            status_callback,
            exception_callback
        )

        self.hardware_monitor_logging = Reporting_Logging(
            settings.hardware_monitor_database_name,
            settings.hardware_monitor_database_fields,
            status_callback,
            exception_callback
        )

        self.start()

    def ensure_database_exists(self):
        pass

    def report_exception_details(self):
        caller_ref = inspect.stack()[1]
        exc_type, exc_value, exc_traceback = sys.exc_info()
        frame = inspect.currentframe().f_back
        parameter_names = frame.f_code.co_varnames[:frame.f_code.co_argcount]
        argument_values = {
            param_name: str(frame.f_locals[param_name])
            for param_name in parameter_names
        }
        exception_details = {
            "time_epoch":time.time(),
            "hostname":socket.gethostname(),
            "path":os.path.realpath(__file__),
            "script_name":str(caller_ref.filename),
            "class_name":str(caller_ref.frame.f_locals["self"].__class__.__name__) if "self" in caller_ref.frame.f_locals else "",
            "method_name":str(caller_ref.function),
            "line_number":int(caller_ref.lineno),
            "args":argument_values,
            "exception_type":exc_type,
            "exception_message":exc_value,
        }
        self.add_to_message_queue("exceptions", exception_details)

    def report_status(self,status_message):
        caller_ref = inspect.stack()[1]
        status_details = {
            "time_epoch":time.time(),
            "hostname":socket.gethostname(),
            "path":os.path.realpath(__file__),
            "script_name":str(caller_ref.filename),
            "class_name":str(caller_ref.frame.f_locals["self"].__class__.__name__) if "self" in caller_ref.frame.f_locals else "",
            "method_name":str(caller_ref.function),
            "line_number":int(caller_ref.lineno),
            "status_message":status_message,
        }
        self.add_to_message_queue("status", status_details)

    def set_all_systems_initialized(self):
        # to do: make thread safe with lock
        self.all_systems_initialized = True

    def add_to_message_queue(self, message_type, message):
        self.message_queue.put((message_type, message))

    def forward_all_unforwarded_messages(self)
        # to do
        pass

    def run(self):
        while True:
            message_type, message = self.message_queue.get(True)
            if message_type == "exceptions":
                self.exception_logging.insert(message_type, message)
                if self.print_exceptions_to_stdout:
                    print(message)
            if message_type == "status":
                self.status_logging.insert(message_type, message)
            if message_type == "hardware_monitor":
                self.hardware_monitor_logging.insert(message_type, message)
            if self.all_systems_initialized:
                if message_type == "exceptions":
                    self.add_to_upstream_message_queue(self.hostname, topics.EXCEPTION, verbs.PUSH, message, time.time())
                if message_type == "status":
                    self.add_to_upstream_message_queue(self.hostname, topics.STATUS, verbs.PUSH, message, time.time())
                if message_type == "hardware_monitor":
                    self.add_to_upstream_message_queue(self.hostname, topics.HARDWARE_MONITOR, verbs.PUSH, message, time.time())





##########################
##### N E T W O R K  #####
##########################

##### N E T W O R K  D I S C O V E R Y  R E S P O N D E R #####

class Network_Discovery_Responder(threading.Thread):
    def __init__(
            self, 
            hostname,
            local_ip, 
            discovery_multicast_group, 
            discovery_multicast_port, 
            discovery_response_port, 
            discovery_update_receiver,
            caller_period):
    
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.local_ip = local_ip
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.discovery_update_receiver = discovery_update_receiver
        self.caller_period = caller_period

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((discovery_multicast_group, discovery_multicast_port))
        self.multicast_request = struct.pack("4sl", socket.inet_aton(discovery_multicast_group), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.multicast_request)

    def response(self, remoteIP, msg_json): 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((remoteIP,self.discovery_response_port))
            s.listen(1)
            connection, ip_address = s.accept()
            with connection:
                print('Connected by', ip_address)
                while True:
                    connection.sendall(msg_json)

    def run(self):
        while True:
                msg_json = self.sock.recv(1024)
                msg_d = yaml.safe_load(msg_json)
                remoteIP = msg_d["ip"]
                print("remote ip discovered by thirtybirds:",remoteIP)
                msg_d["status"] = "device_discovered"
                if self.discovery_update_receiver:
                    resp_d = self.discovery_update_receiver(msg_d)
                resp_json = json.dumps({"ip":self.local_ip,"hostname":socket.gethostname()})
                resp_json = str.encode(resp_json)
                self.response(remoteIP,resp_json)





##### N E T W O R K  D I S C O V E R Y  C A L L E R #####

class Network_Discovery_Caller_Send(threading.Thread):
    def __init__(
            self, 
            local_hostname, 
            local_ip,
            discovery_multicast_group, 
            discovery_multicast_port, 
            caller_period
        ):
        threading.Thread.__init__(self)
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.caller_period = caller_period
        self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self.msg_d = {"ip":local_ip,"hostname":local_hostname}
        self.msg_json = json.dumps(self.msg_d)
        self.mcast_msg = bytes(self.msg_json, 'utf-8')
        self.active = True
        self.lock = threading.Lock()
    def set_active(self,val):
        self.lock .acquire()
        self.active = val
        self.lock .release()
    def run(self):
        while True:
            self.lock .acquire()
            active = bool(self.active)
            self.lock .release()
            if active == True:
                self.multicast_socket.sendto(self.mcast_msg, (self.discovery_multicast_group, self.discovery_multicast_port))
            time.sleep(self.caller_period)

class Network_Discovery_Caller_Recv(threading.Thread):
    def __init__(self, recv_port, discovery_update_receiver, caller_send):
        threading.Thread.__init__(self)
        self.discovery_update_receiver = discovery_update_receiver
        self.caller_send = caller_send
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.connect(("tcp://*:%d", recv_port))

    def run(self):
        while True:
            msg_json = self.listen_sock.recv()
            msg_d = yaml.safe_load(msg_json)
            msg_d["status"] = "device_discovered"
            if self.discovery_update_receiver:
                self.discovery_update_receiver(msg_d)





##### N E T W O R K  D I S C O V E R Y  #####

class Network_Discovery():
    def __init__(
            self,
            ip_address,
            hostname
            host_is_controller,
            discovery_method,
            discovery_multicast_group,
            discovery_multicast_port,
            discovery_response_port,
            discovery_caller_interval,
            discovery_events_callback,
            reporting_ref
        ):

        self.ip_address = ip_address
        self.hostname = hostname
        self.host_is_controller = host_is_controller
        self.settings_controller_hostname = settings_controller_hostname
        self.discovery_method = discovery_method
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.discovery_caller_interval = discovery_caller_interval
        self.discovery_events_callback = discovery_events_callback
        self.dashboard_events_callback = dashboard_events_callback
        self.reporting_ref = reporting_ref
        self.role = network_discovery_roles.DISCOVERY_ROLE_RESPONDER if host_is_controller else network_discovery_roles.DISCOVERY_ROLE_CALLER
        self.server_ip = ""


        if self.role == network_discovery_roles.DISCOVERY_ROLE_RESPONDER:
            self.responder = Responder(
                self.hostname,
                self.ip_address,
                self.discovery_multicast_group,
                self.discovery_multicast_port, 
                self.discovery_response_port,
                self.discovery_events_callback,
                self.discovery_caller_interval
            )
            self.responder.daemon = True
            self.responder.start()

        if self.role == network_discovery_roles.DISCOVERY_ROLE_CALLER:
            self.caller_send = Caller_Send(
                self.hostname, 
                self.ip_address, 
                self.discovery_multicast_group, 
                self.discovery_multicast_port,
                self.discovery_caller_interval
            )
            self.caller_recv = Caller_Recv(
                self.discovery_response_port, 
                self.discovery_events_callback, 
                self.caller_send
            )
            self.caller_recv.daemon = True
            self.caller_send.daemon = True
            self.caller_recv.start()
            self.caller_send.start()





##### N E T W O R K  C O N N E C T I O N  #####

class Network_Connection(threading.Thread):
    def __init__(
            self,
            online_status_mode_callback,
            online_status_polling_interval,
            reporting_ref
        ):
        threading.Thread.__init__(self)
        self.online_status_mode_callback = online_status_mode_callback
        self.online_status_polling_interval = online_status_polling_interval
        self.exception_callback = exception_callback
        self.status_callback = status_callback
        self.online_status = False
        self.start()

    def list_network_interfaces(self):
        return netifaces.interfaces()

    def get_network_interface(self):
        # to do
        pass 

    def set_network_interface(self):
        # to do
        pass 

    def get_local_ip_address(self):
        for iface in interface_names:
            try:
                ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
                if ip[0:3] in ["127","10."]:
                    return ip
            except:
                reporting_ref.report_exception_details()
        return False

    def get_global_ip_address(self):
        try:
            return requests.get('http://ip.42.pl/raw').text
        except Exception as e:
            reporting_ref.report_exception_details()
            return False

    def get_online_status(self):
        return True if len(netifaces.gateways()["default"]) > 0 else False

    def run(self):
        while True:
            time.sleep(self.online_status_polling_interval)
            try:
                online_status = self.get_online_status()
                if online_status != self.online_status:
                    self.online_status = online_status
                    self.online_status_mode_callback(self.online_status)
            except:
                reporting_ref.report_exception_details()





##### N E T W O R K #####

class Network:
    """
    This class manages four network layers:
        online_status
        network_discovery
        duplex_sockets
        pubsub
    
    """
    def __init__(
            settings_controller_hostname,
            discovery_method,
            discovery_multicast_group,
            discovery_multicast_port,
            discovery_response_port,
            discovery_caller_interval,
            heartbeat_interval,
            heartbeat_timeout_factor,
            pubsub_publish_port,
            pubsub_keepalive_interval,
            online_status_polling_interval,
            default_network_interface,
            all_connected_callback,
            network_status_change_callback,
            discovery_events_callback,
            dashboard_events_callback,
            pubsub_message_callback,
            reporting_ref,
        )

        self.settings_controller_hostname = settings_controller_hostname
        self.discovery_method = discovery_method
        self.discovery_multicast_group = discovery_multicast_group
        self.discovery_multicast_port = discovery_multicast_port
        self.discovery_response_port = discovery_response_port
        self.discovery_caller_interval = discovery_caller_interval
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout_factor = heartbeat_timeout_factor
        self.pubsub_publish_port = pubsub_publish_port
        self.pubsub_keepalive_interval = pubsub_keepalive_interval
        self.reporting_ref = reporting_ref
        self.online_status_polling_interval = online_status_polling_interval
        self.default_network_interface = default_network_interface
        self.all_connected_callback = all_connected_callback
        self.network_status_change_callback = network_status_change_callback
        self.discovery_events_callback = discovery_events_callback
        self.pubsub_message_callback = pubsub_message_callback
        self.dashboard_events_callback = dashboard_events_callback

        self.host_is_controller = True if self.hostname==settings_controller_hostname else False

    def get_hostname(self):
        try:
            return socket.gethostname()
        except Exception:
            reporting_ref.report_exception_details()
            return False

    def network_connection = Network_Connection(
            network_status_change_callback, # to do: create method in this class?
            online_status_polling_interval, # to do: create method in this class?
            reporting_ref
        )

    def network_discovery = Network_Discovery(
            network_status_change_callback, # to do: create method in this class?
            online_status_polling_interval, # to do: create method in this class?
            reporting_ref
        )


class Thirtybirds(threading.Thread):
    def __init__(
            self,
            app_settings,
            pubsub_message_callback,
            exception_callback,
            discovery_events_callback = None,
            all_connected_callback = None,
            status_callback = None,
            network_status_change_callback = None,
            dashboard_events_callback = None,
            hardware_warning_callback = None,
            version_control_callback = None
        ):
        threading.Thread.__init__(self)
        self.message_queue = queue.Queue()
        self.thread_start_timestamp = time.time()
        self.settings = collate_settings(tb_settings, app_settings)
        self.app_path = os.path.dirname(os.path.realpath(__main__))
        self.hostname = socket.gethostname()


        ### SCOPE ARGUMENTS TO SELF ###
        ###############################
        self.all_connected_callback = all_connected_callback
        self.discovery_events_callback = discovery_events_callback
        self.network_status_change_callback = network_status_change_callback
        self.pubsub_message_callback = pubsub_message_callback
        self.dashboard_events_callback = dashboard_events_callback
        self.exception_callback = exception_callback
        self.status_callback = status_callback
        self.hardware_warning_callback = hardware_warning_callback


        ### INTERPRET COMMAND LINE ARGUMENTS ###
        ########################################
        self.interpret_command_line_flags()
        self.host_is_controller = True if self.hostname==self.settings.controller_hostname else False


        ### REPORTING ###
        #################
        self.logfile_path = self.settings.logfile_path
        self.reporting = Reporting(
                self.settings.start_web_interfaces,
                self.settings.http_port,
                self.settings.websocket_port,
                self.settings.refresh_interval,
                self.settings.exceptions_database_name,
                self.settings.exceptions_database_fields,
                self.settings.status_database_name,
                self.settings.status_database_field,
                self.settings.hardware_monitor_database_name,
                self.settings.hardware_monitor_database_field,
                self.logfile_path,
                self.add_to_message_queue,
            )


        ### NETWORKING ###
        ##################
        self.network = Network(
                self.settings.controller_hostname
                self.settings.discovery_method,
                self.settings.discovery_multicast_group,
                self.settings.discovery_multicast_port,
                self.settings.discovery_response_port,
                self.settings.discovery_caller_interval,
                self.settings.heartbeat_interval,
                self.settings.heartbeat_timeout_factor,
                self.settings.pubsub_publish_port,
                self.settings.pubsub_keepalive_interval,
                self.settings.online_status_polling_interval,
                self.settings.default_network_interface,
                self.all_connected_callback,
                self.network_status_change_callback,
                self.discovery_events_callback,
                self.dashboard_events_callback
                self.add_to_message_queue,
                self.reporting,
            )
        self.hostname = host_info.get_hostname()


        ### PROCESS CONTROL ###
        #######################
        self.processes_control = Process_Control(
                self.exception_callback,
                self.status_callback,
            )


        ### SOFTWARE MONITOR ###
        ########################
        self.software_monitor = Software_Monitor(
                self.app_path,
                self.settings.app_repo_name,
                self.settings.app_branch
                self.settings.thirtybirds_repo_owner,
                self.settings.thirtybirds_repo_name,
                self.settings.thirtybirds_branch,
                self.settings.software.update_on_start,
                self.processes_control,
                self.add_to_message_queue,
                self.exception_callback,
                self.status_callback,
            )
            # to do: get OS and version on request


        ### HARDWARE MONITOR ###
        ########################
        self.hardware_monitor = Hardware_Monitor(
                self.settings.hardware_measurements_interval,
                self.settings.nominal_range_core_temp,
                self.settings.nominal_range_core_voltage,
                self.settings.nominal_min_memory_free,
                self.settings.nominal_min_system_disk,
                self.settings.nominal_min_wifi_strength,
                self.add_to_message_queue,
                self.exception_callback,
                self.status_callback,
            )
            # to do: get hardware platform on request

        self.reporting.set_all_systems_initialized()

    def collate_settings(self, base_settings_module, optional_settings_module):
        base_settings_classnames = [i for i in dir(base_settings_module) if not (i[:2]=="__" and i[-2:]=="__")] 
        optional_settings_classnames = [i for i in dir(optional_settings_module) if not (i[:2]=="__" and i[-2:]=="__")]
        for optional_settings_class in optional_settings_classnames:
            if optional_settings_class not in base_settings_classnames:
                setattr(base_settings_module, optional_settings_class, getattr(optional_settings_module, optional_settings_class))
            else:
                base_settings_class_ref = getattr(base_settings_module, optional_settings_class)
                optional_settings_class_ref = getattr(optional_settings_module, optional_settings_class)
                # todo: it would be more concise and idiomatic to do the following with multiple inheritance.  if possible.
                optional_settings_class_variable_names = [attr for attr in dir(optional_settings_class_ref) if not callable(getattr(optional_settings_class_ref, attr)) and not attr.startswith("__")]
                for optional_settings_class_variable_name in optional_settings_class_variable_names:
                    setattr(base_settings_class_ref, optional_settings_class_variable_name, getattr(optional_settings_class_ref, optional_settings_class_variable_name))
        return base_settings_module


    def interpret_command_line_flags(self):
        try:
            sys.argv[sys.argv.index("-help")]
            print("thirtybirds command line options:")
            print("  -hostname $hostname")
            print("    run as specified $hostname")
            print("  -update_on_start [true|false]")
            print("    run all version updates specified in settings")
            sys.exit(0)
        except ValueError:
            pass

        try:
            self.hostname = sys.argv[sys.argv.index("-hostname")+1]
        except ValueError as e:
            pass
        except IndexError as e:
            print("usage: python ____.py -hostname $hostname")
            sys.exit(0)

        try:
            update_on_start_bool = sys.argv[sys.argv.index("-update_on_start")+1]
            self.update_on_start = True if update_on_start_bool in [1,"true","True"] else False
        except ValueError as e:
            pass
        except IndexError as e:
            print("usage: python ____.py -update_on_start [true|false]")
            sys.exit(0)


    def add_to_message_queue(self, origin_hostname, topic, verb, data, timestamp):
        """
        tb message types = [EXCEPTION, ERROR, STATUS, THIRTYBIRDS, NETWORK_STATUS_CHANGE]
        each app has its own message types
            is "" an option?

        hostname can be local, remote, or dashboard
        """
        self.message_queue.put((origin_hostname, topic, verb, data, timestamp))

    def run(self):
        while True:
            try:
                origin_hostname, topic, verb, data, timestamp = self.message_queue.get(True)



def init(
        app_settings,
        pubsub_message_callback,
        exception_callback,
        all_connected_callback = None,
        dashboard_events_callback = None,
        discovery_events_callback = None,
        hardware_warning_callback = None,
        network_status_change_callback = None,
        status_callback = None,
        version_control_callback = None
    ):  
    def dummy_callback(x*):
        pass

    thirtybirds = Thirtybirds(
            app_settings,
            pubsub_message_callback,
            exception_callback if exception_callback is not None else dummy_callback,
            all_connected_callback if all_connected_callback is not None else dummy_callback,
            dashboard_events_callback if dashboard_events_callback is not None else dummy_callback,
            discovery_events_callback if discovery_events_callback is not None else dummy_callback,
            hardware_warning_callback if hardware_warning_callback is not None else dummy_callback,
            network_status_change_callback if network_status_change_callback is not None else dummy_callback,
            status_callback if status_callback is not None else dummy_callback,
            version_control_callback if version_control_callback is not None else dummy_callback
        )

    class API:
        # to do: update after refactoring systems
        ## N E T W O R K I N G ##
        get_all_connected = thirtybirds.network.get_all_connected
        get_global_ip = thirtybirds.network.get_global_ip
        get_hostname = thirtybirds.network.get_hostname
        get_local_ip = thirtybirds.network.get_local_ip
        get_network_interface = thirtybirds.network.get_network_interface
        get_network_mode = thirtybirds.network.get_network_mode
        get_online_status = thirtybirds.network.get_online_status
        get_topic_type = thirtybirds.network.get_online_status
        list_connection_status = thirtybirds.network.list_connection_status
        list_subscribed_topics = thirtybirds.network.list_subscribed_topics
        publish = thirtybirds.network.publish
        set_fake_hostname = thirtybirds.network.set_fake_hostname
        set_fake_hostname = thirtybirds.network.set_fake_hostname
        set_network_mode = networking.set_network_mode
        start_network_discovery = thirtybirds.network.start_network_discovery
        stop_network_discovery = thirtybirds.network.stop_network_discovery
        subscribe_to_topic = thirtybirds.network.subscribe_to_topic
        unsubscribe_from_topic = thirtybirds.network.unsubscribe_from_topic

        ## P R O C E S S E S ##
        get_app_runtime = thirtybirds.processes.get_app_runtime
        get_os_uptime = thirtybirds.processes.get_os_uptime
        get_os_version = thirtybirds.processes.get_os_version
        reboot = thirtybirds.processes.reboot
        restart_service = thirtybirds.processes.restart_service
        shutdown = thirtybirds.processes.shutdown

        ## S O F T W A R E   M O N I T O R ##
        app_get_git_timestamp = thirtybirds.software_monitor.app_get_git_timestamp
        app_get_scripts_version = thirtybirds.software_monitor.app_get_scripts_version
        app_pull_from_github = thirtybirds.software_monitor.app_pull_from_github
        app_run_update_scripts = thirtybirds.software_monitor.app_run_update_scripts
        tb_get_git_timestamp = thirtybirds.software_monitor.tb_get_git_timestamp
        tb_get_scripts_version = thirtybirds.software_monitor.tb_get_scripts_version
        tb_pull_from_github = thirtybirds.software_monitor.tb_pull_from_github
        tb_run_update_scripts = thirtybirds.software_monitor.tb_run_update_scripts

        ## H A R D W A R E   M O N I T O R ##
        get_core_temp = thirtybirds.hardware_monitor.get_core_temp
        get_core_voltage = thirtybirds.hardware_monitor.get_core_voltage
        get_memory_free = thirtybirds.hardware_monitor.get_memory_free
        get_system_cpu = thirtybirds.hardware_monitor.get_system_cpu
        get_system_disk = thirtybirds.hardware_monitor.get_system_disk
        get_system_status = thirtybirds.hardware_monitor.get_system_status
        get_system_uptime = thirtybirds.hardware_monitor.get_system_uptime
        get_wifi_strength = thirtybirds.hardware_monitor.get_wifi_strength

        ##  R E P O R T I N G ##
        forward_log_to_controller = thirtybirds.reporting.forward_log_to_controller
        handle_forwarded_log_events = thirtybirds.reporting.handle_forwarded_log_events
        log = thirtybirds.reporting.log
        log_exception = thirtybirds.reporting.log_exception
        log_status = thirtybirds.reporting.log_status
        set_forwarding_connected_status = thirtybirds.reporting.set_forwarding_connected_status

    return API





