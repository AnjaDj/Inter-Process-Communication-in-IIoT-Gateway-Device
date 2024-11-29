import json

INT32_MIN = -2**31
INT32_MAX = 2**31 - 1

def read_contact_number_from_config_file(file_path):
    try:

        with open(file_path, 'r') as config_file:
            configuration = json.load(config_file)

        contact_number = configuration.get("contact_number")

        # Checks whether the contact number is integer 32bit
        if isinstance(contact_number, int) and INT32_MIN <= contact_number <= INT32_MAX:
            return contact_number
        else:
            raise ValueError(f"Contact number in '{file_path}' is not a valid int32 value.")
            
    except FileNotFoundError:
        raise FileNotFoundError(f"'{file_path}' not found.")
    
    except PermissionError:
        raise PermissionError(f"Permission denied - attempt to access '{file_path}' without proper permissions.")
    
    except IOError as e:
        raise IOError(f"An error occurred while opening the file '{file_path}' : {e}")
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in '{file_path}' file : {e}")
        
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
        
def read_server_address_from_config_file(file_path, server):
    try:
    
        with open(file_path, 'r') as config_file:
            configuration = json.load(config_file)

        server_address = None
        
        if server == 'main':
            server_address = configuration.get("main_server_address")
        elif server == 'modem':
            server_address = configuration.get("modem_server_address")

        return server_address

    except FileNotFoundError:
        raise FileNotFoundError(f"'{file_path}' not found.")
    
    except PermissionError:
        raise PermissionError(f"Permission denied - attempt to access '{file_path}' without proper permissions.")
    
    except IOError as e:
        raise IOError(f"An error occurred while opening the file '{file_path}' : {e}")
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in '{file_path}' file : {e}")
        
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
