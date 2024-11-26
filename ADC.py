import os
import time
import grpc
import logging
import threading
import objectProximityDetectionService_pb2
import objectProximityDetectionService_pb2_grpc

# Configure logging
logging.basicConfig(filename='ADC.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

ADC_DRIVER_DEVICE = "/dev/ADC_driver"	# device path, path to the driver file
end_program = False 					# flag to end the program
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
    Reads and Interprets data from ADC
    
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
    Sends gRPC message if nearby object has been detected.
    
    :param : None
    :return: None		
"""
def sensor_run():
    
    global adc_fd, stub, end_program    # Access global variables
    THRESHOLD = 0x00000401 				# Define the threshold for detecting objects

    # Open ADC driver
    adc_fd = open_driver(ADC_DRIVER_DEVICE)
    if adc_fd is None:
        return 
        
    # Connect to the local Main gRPC server    
    try:
        with grpc.insecure_channel('127.0.0.1:50051') as channel:
            stub = objectProximityDetectionService_pb2_grpc.ObjectProximityDetectionServiceStub(channel)
    except grpc.RpcError as e:
        logging.critical(f"ADC gRPC-client failed to connect to the main gRPC-server: {e}")
        print(f"ADC gRPC-client failed to connect to the main gRPC-server: {e}\n")
    finally:
        close_driver(adc_fd)
        
        
    while not end_program:
        data = read_adc(adc_fd, 4)

        if data > THRESHOLD:
            logging.info("Object Detected. ADC gRPC-client sends gRPC-request to Main gRPC-server.")
            print("Object Detected. ADC gRPC-client sends gRPC-request to Main gRPC-server.\n")
            request  = objectProximityDetectionService_pb2.ObjectProximityDetectionRequest(message="Object Detected",object_proximity_distance=data)
            response = stub.ObjectProximityDetection(request)
            logging.info(f"ADC gRPC client received gRPC reply from Main gRPC-server: {response.message}")
            print(f"ADC gRPC client received gRPC reply from Main gRPC-server: {response.message}\n")
        
        time.sleep(100 / 1000) #100ms
    
    close_driver(adc_fd)
			

# Start a thread to handle sensor data
sensor_thread = threading.Thread(target=sensor_run)
sensor_thread.start()
