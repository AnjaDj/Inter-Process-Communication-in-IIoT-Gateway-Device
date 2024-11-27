import json

INT32_MIN = -2**31
INT32_MAX = 2**31 - 1

def read_contact_number_from_config_file(file_path):
    try:

        with open(file_path, 'r') as config_file:
            config = json.load(config_file)

        contact_number = config.get("contact_number")

        # Checks whether the contact number is integer 32bit
        if isinstance(contact_number, int) and INT32_MIN <= contact_number <= INT32_MAX:
            return contact_number
        else:
            raise ValueError("Contact number is not a valid int32 value.")
            
    except FileNotFoundError:
        print(f"Error: Configuration file '{file_path}' not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in configuration file.")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        
def read_server_address_from_config_file(file_path, server):
    try:
    
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)

        server_address = None
        
        if server == 'main':
            server_address = config.get("main_server_address")
        elif server == 'modem':
            server_address = config.get("modem_server_address")

        return server_address

    except FileNotFoundError:
        print(f"Error: Configuration file '{file_path}' not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in configuration file.")
    except Exception as e:
        print(f"Unexpected error: {e}")
