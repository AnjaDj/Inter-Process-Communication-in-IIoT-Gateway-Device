"""ADC.py

This Python script implements several functionalities:

    1. Communication with the DRIVER (/dev/ADC_driver) via following functions
        - open_driver(device_path) 
        - close_driver(fd) 
        - read_adc(fd, num_bytes)
    2. Reading and interpreting raw data got from ADC
        - read_adc(fd, num_bytes)
    3. Establishing gRPC communication with the Main gRPC-server
    
Scripts assignment is to read raw data got from ADC, interpret it and if
nearby object has been detected, to send gRPC-request to Main gRPC-server

"""

import os
import time
import grpc
import logging
import threading
import config
import objectProximityDetectionService_pb2
import objectProximityDetectionService_pb2_grpc

# Configure logging
logging.basicConfig(filename='ADC.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# path to the config file in JSON format                    
config_path = "config_adc.json"

ADC_DRIVER_DEVICE = "/dev/ADC_driver"	# device path to the driver file
main_server_address = None
channel     = None
adc_fd      = None						# file descriptor
stub        = None

"""
    Opens driver and returns file descriptor (fd)
    
    :param device_path: Path to driver file (e.g. /dev/mydevice)
    :return:            File descriptor (fd) or None if failed to open 
"""
def open_driver(device_path):
    try:
        fd = os.open(device_path, os.O_RDWR) 
        logging.info(f"Driver {device_path} opened successfully. File descriptor: {fd}.")
        print(f"Driver {device_path} opened successfully. File descriptor: {fd}.\n")
        return fd
    except OSError as e:
        logging.critical(f"Failed to open driver {device_path}: {e}.")
        print(f"Failed to open driver {device_path}: {e}.\n")
        return None


"""
    Closes driver
    
    :param fd: File descriptor (fd)
"""
def close_driver(fd):
    try:
        os.close(fd)
        logging.info(f"Driver {fd} closed successfully.")
        print(f"Driver {fd} closed successfully.\n")
    except OSError as e:
        logging.critical(f"Failed to close driver {fd}: {e}.")
        print(f"Failed to close driver {fd}: {e}.\n")


"""
    Reads and Interprets raw data got from ADC
    
    :param fd: 			File descriptor
    :param num_bytes: 	Number of bytes to be read
    :return: 			Integer data received from ADC
"""
def read_adc(fd, num_bytes):
    try:
		# data_raw is an array of num_bytes bytes - raw binary bytes received from ADC driver
        data_raw = os.read(fd, num_bytes)

        # Interpretation of array of bytes into integer
        data_num = int.from_bytes(data_raw, byteorder='little')  # little-endian format

        logging.info(f"Data received from ADC: {data_num}.")
        print(f"Data received from ADC: {data_num}.\n")
        return data_num
        
    except OSError as e:
        logging.error(f"Failed to receive data from ADC: {e}.")
        print(f"Failed to receive data from ADC: {e}.\n")
        return None


"""
    Checks whether a nearby object has been detected.
    Sends gRPC-request to the Main gRPC-server if nearby object has been detected.
    
    :param : None
    :return: None		
"""
def sensor_run():
    
    global adc_fd, stub, channel   # Access global variables
    THRESHOLD = 0x00000401 		   # Define the threshold for detecting objects at any distance

    # Open ADC driver
    adc_fd = open_driver(ADC_DRIVER_DEVICE)
    if adc_fd is None:
        return 
        
    # Connect to the local Main gRPC-server    
    server_address = config_data.read_server_address_from_config_file(config_path, 'main')
    
    try:
        channel = grpc.insecure_channel(server_address)
        stub    = objectProximityDetectionService_pb2_grpc.ObjectProximityDetectionServiceStub(channel)
    except grpc.RpcError as e:
        logging.critical(f"ADC gRPC-client failed to connect to the Main gRPC-server: {e}")
        print(f"ADC gRPC-client failed to connect to the Main gRPC-server: {e}\n")
    finally:
        close_driver(adc_fd)
        
        
    while True:
        data = read_adc(adc_fd, 4)

        if data > THRESHOLD:
            logging.info("Object Detected. ADC gRPC-client sends gRPC-request to Main gRPC-server.")
            print("Object Detected. ADC gRPC-client sends gRPC-request to Main gRPC-server.\n")
            
            request  = objectProximityDetectionService_pb2.ObjectProximityDetectionRequest(message="Object Detected",object_proximity_distance=data)
            reply    = stub.ObjectProximityDetection(request)
            
            logging.info(f"ADC gRPC client received gRPC-reply from Main gRPC-server: {reply.message}")
            print(f"ADC gRPC client received gRPC-reply from Main gRPC-server: {reply.message}\n")
        
        time.sleep(100 / 1000) #100ms
    
    close_driver(adc_fd)
			

def test():
    global stub, channel  
    data = 1500				            

    try:
        while True:
            logging.info(f"Object Detected: ADC gRPC-client sends gRPC-request to Main gRPC-server. Message: object_proximity_distance = {data}")
                
            request  = objectProximityDetectionService_pb2.ObjectProximityDetectionRequest(message="Object Detected",object_proximity_distance=data)
            reply    = stub.ObjectProximityDetection(request)
                
            logging.info(f"ADC gRPC-client received gRPC-reply from Main gRPC-server: {reply.message}")
            
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("ADC gRPC-client is shuting down.")
        channel.close()
        return   

def use_MAIN(max_retries=3):
    
    attempt = 1
    while attempt <= max_retries:
        try:
            global stub, channel, main_server_address
            
            main_server_address = config.get_config(config_path, 'main')
            connection_time     = config.get_config(config_path, 'connection_time')
            
            logging.info(f"ADC gRPC-client trying to connect to the Main gRPC-server running on {main_server_address}...")
            
            # Creates channel
            channel = grpc.insecure_channel(main_server_address)
            # Checks if channel is ready for communication
            grpc.channel_ready_future(channel).result(timeout=connection_time)
            # Stub creating
            stub    = objectProximityDetectionService_pb2_grpc.ObjectProximityDetectionServiceStub(channel)
            
            logging.info(f"ADC gRPC-client connected to the Main gRPC-server running on {main_server_address}.")
            return
            
        except grpc.FutureTimeoutError:
            logging.error(f"Timeout limit exceeded. ADC gRPC-client couldnt establish connection with Main gRPC-server running on {main_server_address}")
        except grpc.RpcError as e:
            logging.error(f"RPC error occurred at ADC - MAIN line : {e.code()} - {e.details()}")
        except Exception as e:
            logging.error(f"ADC gRPC-client failed to connect to the Main gRPC-server running on {main_server_address}: {e}")
            
        attempt += 1
        
        if attempt <= max_retries:
            logging.warning(f"ADC Retrying to connect to the Main gRPC-server running on {main_server_address} in 3 seconds...")
            time.sleep(3)
        else:
            logging.critical(f"ADC reached max connection retries. Unable to connect to the Main gRPC-server running on {main_server_address}  after multiple attempts")
            if 'channel' in globals() and channel is not None:
                channel.close()
            raise RuntimeError("ADC failed to connect to the Main gRPC-server after multiple attempts.")
        
use_MAIN()
# Start a thread to handle sensor data
sensor_thread = threading.Thread(target=test)
sensor_thread.start()
