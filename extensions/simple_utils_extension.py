import datetime

from .jess_extension import jess_extension


@jess_extension(
    description="Get current date/time",
    param_descriptions={}
)
def current_date_time():
    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time in a readable format
    return now.strftime("%Y-%m-%d %H:%M:%S")
