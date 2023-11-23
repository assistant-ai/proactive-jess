import yaml
from .memory_extension import Memory
from .google_calendar_extension import get_upcoming_calendar_events, create_google_calendar_event
from .simple_utils_extension import current_date_time
from .local_bash_extension import send_bash_command_to_local_host

def _read_config():
    with open("./config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_extensions():
    config = _read_config()

    extensions = {}

    if config["extensions"]["long_term_memory"]:
        memory = Memory.create_memory_extension()
        extensions["store_in_long_term_memory"] = memory.store_in_long_term_memory
        extensions["query_from_long_term_memory"] = memory.query_from_long_term_memory
    if config["extensions"]["google_calendar"]:
        extensions["get_upcoming_calendar_events"] = get_upcoming_calendar_events
        extensions["create_google_calendar_event"] = create_google_calendar_event
    if config["extensions"]["current_date_time"]:
        extensions["current_date_time"] = current_date_time
    if config["extensions"]["local_bash"]:
        extensions["send_bash_command_to_local_host"] = send_bash_command_to_local_host
    return extensions