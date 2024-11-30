import json

INT32_MIN = -2**31
INT32_MAX = 2**31 - 1

def get_config(file_path, key):
    try:
    
        with open(file_path, 'r') as config_file:
            configuration = json.load(config_file)

        config_value = None
        
        if key == 'main':
            config_value = configuration.get("main_server_address")
        elif key == 'modem':
            config_value = configuration.get("modem_server_address")
        elif key == 'contact':
            config_value = configuration.get("contact_number")
            if not isinstance(config_value, int) or not(INT32_MIN <= config_value <= INT32_MAX):
                raise ValueError(f"Contact number in '{file_path}' is not a valid int32 value.")
        elif key == 'threshold0':
            config_value = configuration.get("THRESHOLD0")
            if not isinstance(config_value, int) or not(INT32_MIN <= config_value <= INT32_MAX):
                raise ValueError(f"Threshold value in '{file_path}' is not a valid int32 value.")
        elif key == 'threshold1':
            config_value = configuration.get("THRESHOLD1")
            if not isinstance(config_value, int) or not(INT32_MIN <= config_value <= INT32_MAX):
                raise ValueError(f"Threshold valuein '{file_path}' is not a valid int32 value.")
        elif key == 'connection_time':
            config_value = configuration.get("connection_time")
            if not isinstance(config_value, int) or not(INT32_MIN <= config_value <= INT32_MAX):
                raise ValueError(f"Threshold valuein '{file_path}' is not a valid int32 value.")
        else:
            raise ValueError(f"Invalid key-search format in '{file_path}' file: Searched for {key}")
            
        if config_value is not None:
            return config_value
        else:
            raise ValueError(f"An error occurred while getting config data - {key} from {file_path}")

    except FileNotFoundError:
        raise FileNotFoundError(f"'{file_path}' not found.")
    
    except PermissionError:
        raise PermissionError(f"Permission denied - attempt to access '{file_path}' without proper permissions.")
    
    except IOError as e:
        raise IOError(f"An error occurred while opening the file '{file_path}' : {e}")
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in '{file_path}' file : {e}")
        
    except Exception:
        raise
