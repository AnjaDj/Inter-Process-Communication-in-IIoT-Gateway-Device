import os
import time
import grpc
import threading
import service_pb2
import service_pb2_grpc

ADC_DRIVER_DEVICE = "/dev/ADC_driver"	# device path, path to the driver file
adc_fd = None							# file descriptor
stub   = None
end_program = False 					# flag to end the program

"""
    Opens driver and returns file descriptor (fd)
    
    :param device_path: Path to driver file (e.g. /dev/mydevice)
    :return:            File descriptor (fd) or None if failed to open 
"""
def open_driver(device_path):
    try:
        fd = os.open(device_path, os.O_RDWR) 
        print(f"Driver {device_path} opened successfully. File descriptor: {fd}.")
        return fd
    except OSError as e:
        print(f"Failed to open driver {device_path}: {e}.")
        return None


"""
    Closes driver
    
    :param fd: File descriptor (fd)
"""
def close_driver(fd):
    try:
        os.close(fd)
        print(f"Driver {fd} closed successfully.")
    except OSError as e:
        print(f"Failed to close driver {fd}: {e}.")


"""
    Reads data from ADC
    
    :param fd: 			File descriptor
    :param num_bytes: 	Number of bytes to be read
    :return: 			Data read from driver
"""
def read_adc(fd, num_bytes):
    try:
		# data_raw is an array of num_bytes bytes - raw binary bytes read from ADC
        data_raw = os.read(fd, num_bytes)

        # Interpretation of array of bytes into integer number
        data_num = int.from_bytes(data_raw, byteorder='little')  # 'little' for little-endian format

        print(f"Read data from ADC: {data_num}")
        return data_num
        
    except OSError as e:
        print(f"Failed to read from ADC driver: {e}")
        return None


"""
    Gets data from ADC and checks whether a nearby object has been detected.
    Sends gRPC message if nearby object has been detected.
"""
def sensor_run():
	
    THRESHOLD = 0x00000401 				# Define the threshold for detecting objects
    global adc_fd, stub, end_program    # Access global variables

    while not end_program:
        data = read_adc(adc_fd, 4)
        if data > THRESHOLD:
            request  = service_pb2.MotionDetectionRequest(name="Motion Detected - Action needed")
            response = stub.MotionDetection(request)
            print(f"Received reply from server: {response.message}")
        time.sleep(100 / 1000) #100ms
			

def run():
    global adc_fd, stub, end_program	# Access global variables

    # Connect to the gRPC server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.MotionDetectionServiceStub(channel)

    # Open ADC driver
    adc_fd = open_driver(ADC_DRIVER_DEVICE)
    if adc_fd is None:
        return 

    # Start a thread to handle sensor data
    sensor_thread = threading.Thread(target=sensor_run)
    sensor_thread.start()

    # Wait for user input to stop the program
    while True:
        user_input = input()
        if user_input == "STOP":
            print("Program ended by user")
            end_program = True
            break

    sensor_thread.join()
    close_driver(adc_fd)
        


if __name__ == '__main__':
    run()
