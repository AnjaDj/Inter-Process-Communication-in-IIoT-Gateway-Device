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
config_path       = "config_adc.json"
ADC_DRIVER_DEVICE = "/dev/ADC_driver"	# device path to the driver file                          
adc_fd      = None						# file descriptor
channel     = None                      # for communication with Main server
stub        = None                      # for communication with Main server

# global configuration data
main_server_address  = None
connection_time      = None
threshold            = None

"""
    Gets configuration data

    :param : None
    :return: None
"""
def get_configs():
    global main_server_address, connection_time, threshold
    
    try:
        main_server_address  = config.get_config(config_path, 'main')
        connection_time      = config.get_config(config_path, 'connection_time')
        threshold            = config.get_config(config_path, 'threshold')
    except Exception as e:
        logging.critical(f"An error occurred while getting config data: {e}")
        raise


"""
    Opens driver and returns file descriptor (fd)
    
    :param device_path: Path to driver file (e.g. /dev/mydevice)
    :return:            File descriptor (fd) or None if failed to open 
"""
def open_driver(device_path):
    try:
        fd = os.open(device_path, os.O_RDWR) 
        logging.info(f"Driver {device_path} opened successfully. File descriptor: {fd}.")
        return fd
    except OSError as e:
        logging.critical(f"Failed to open driver {device_path}: {e}.")
        raise


"""
    Closes driver
    
    :param fd: File descriptor (fd)
"""
def close_driver(fd):
    try:
        os.close(fd)
        logging.info(f"Driver {fd} closed successfully.")
    except OSError as e:
        logging.critical(f"Failed to close driver {fd}: {e}.")
        raise



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
        return data_num
        
    except OSError as e:
        logging.error(f"Failed to receive data from ADC: {e}.")
        return None


"""
    Checks whether a nearby object has been detected.
    Sends gRPC-request to the Main gRPC-server if nearby object has been detected.
    
    :param : None
    :return: None		
"""
def sensor_run():
    
    global adc_fd, stub, channel, threshold   # Access global variables

    # Opens ADC driver
    try:
        adc_fd = open_driver(ADC_DRIVER_DEVICE)
    except Exception:
        raise
     
    try:    
        while True:
            data = read_adc(adc_fd, 4)

            if data > threshold:
                logging.info(f"Object Detected: ADC client sends request to Main server. distance = {data}")
                
                request  = objectProximityDetectionService_pb2.ObjectProximityDetectionRequest(message="Object Detected",object_proximity_distance=data)
                reply    = stub.ObjectProximityDetection(request)
                    
                logging.info(f"ADC client received reply from Main server: {reply.message}")
            
            time.sleep(5)
                
    except KeyboardInterrupt:
        logging.info("ADC client is shuting down.")
        close_driver(adc_fd)
        channel.close()
        return  

def test():
    global stub, channel  
    data = 1500				            

    try:
        while True:
            logging.info(f"Object Detected: ADC client sends request to Main server. Message: object_proximity_distance = {data}")
                
            request  = objectProximityDetectionService_pb2.ObjectProximityDetectionRequest(message="Object Detected",object_proximity_distance=data)
            reply    = stub.ObjectProximityDetection(request)
                
            logging.info(f"ADC client received reply from Main server: {reply.message}")
            
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("ADC client is shuting down.")
        channel.close()
        return   

"""
    Connects to the local main gRPC server
    
    :param max_retries: Max number of connection retries 
    :return: None
"""
def use_MAIN(max_retries=3):
    
    attempt = 1
    global stub, channel, main_server_address, connection_time
    
    while attempt <= max_retries:
        try:
            logging.info(f"ADC client trying to connect to the Main server...")
            
            # Creates channel
            channel = grpc.insecure_channel(main_server_address)
            # Checks if channel is ready for communication
            grpc.channel_ready_future(channel).result(timeout=connection_time)
            # Stub creating
            stub    = objectProximityDetectionService_pb2_grpc.ObjectProximityDetectionServiceStub(channel)
            
            logging.info(f"ADC client connected to the Main server running on {main_server_address}.")
            return
            
        except grpc.FutureTimeoutError:
            logging.error(f"Timeout limit exceeded. ADC client couldnt establish connection with Main server running on {main_server_address}")
        except grpc.RpcError as e:
            logging.error(f"RPC error occurred at ADC - MAIN line : {e.code()} - {e.details()}")
        except Exception as e:
            logging.error(f"ADC client failed to connect to the Main server running on {main_server_address}: {e}")
            
        attempt += 1
        
        if attempt <= max_retries:
            logging.warning(f"ADC Retrying to connect to the Main server running on {main_server_address} in 3 seconds...")
            time.sleep(3)
        else:
            logging.critical(f"ADC reached max connection retries. Unable to connect to the Main server running on {main_server_address}  after multiple attempts!")
            if 'channel' in globals() and channel is not None:
                channel.close()
            raise RuntimeError("ADC failed to connect to the Main server after multiple attempts.")

get_configs()        
use_MAIN()
test()
