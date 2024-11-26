import time
from datetime import datetime
"""
    Creates timestamp
    
    :param : None
    :return: timestamp in the format YYYYMMDDHHMMSS
"""
def create_time_stamp():
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d%H%M%S") # formating
    return timestamp
