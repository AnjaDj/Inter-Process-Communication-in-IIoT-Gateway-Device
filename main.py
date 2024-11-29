"""main.py

This Python script implements several functionalities:

    1. Communication with ADC gRPC-client

    2. Communication with Modem gRPC-server
    
    3. Communication with Camera via D-Bus
    
    4. Reading config file in JSON format in order to get
        - contact number
        - servers addresses
    
Scripts assignment is to receive data from ADC client and depending on 
the proximity of the object, to send gRPC-request to Modem gRPC-server
or to send D-Bus message to Camera

"""

import grpc
import time
import logging
import config
import modemCommunication_pb2
import modemCommunication_pb2_grpc
import objectProximityDetectionService_pb2
import objectProximityDetectionService_pb2_grpc
from concurrent import futures

channel = None # connection to modem gRPC server
stub    = None # connection to modem gRPC server

# Configure logging
logging.basicConfig(filename='main.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
                    
# path to the config file in JSON format                    
config_path = "config_main.json"

class ObjectProximityDetectionServiceServicer(objectProximityDetectionService_pb2_grpc.ObjectProximityDetectionServiceServicer):
    def ObjectProximityDetection(self, request, context):
        
        global stub, channel
        
        logging.info(f"Main gRPC-server received gRPC-request from ADC gRPC-client: request.message={request.message}, request.object_proximity_distance={request.object_proximity_distance}")
        print(f"Main gRPC-server received gRPC-request from ADC gRPC-client: request.message={request.message}, request.object_proximity_distance={request.object_proximity_distance}\n")
        
        ########## OBRADA #############
        THRESHOLD = 0x00000401
        
        if request.object_proximity_distance > THRESHOLD:
            
            logging.info("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.")
            print("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.\n")
            
            number = config.read_contact_number_from_config_file(config_path)
            
            request_for_modem   = modemCommunication_pb2.ModemCommunicationRequest(message="Object Detected",contact_number=number)
            reply_from_modem    = stub.ModemCommunication(request_for_modem)
            
            logging.info(f"Main gRPC-client received gRPC-reply from modem gRPC-server: {reply_from_modem.message}")
            print(f"Main gRPC-client received gRPC-reply from modem gRPC-server: {reply_from_modem.message}\n")
        
        ########## OBRADA #############
        
        reply_for_ADC = "Main gRPC-server took action."
        return objectProximityDetectionService_pb2.ObjectProximityDetectionReply(message=reply_for_ADC)
        

"""
    Sets up and runs a gRPC server for communication with ADC client
    
    :param : None
    :return: None
"""
def serve_ADC():
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        objectProximityDetectionService_pb2_grpc.add_ObjectProximityDetectionServiceServicer_to_server(ObjectProximityDetectionServiceServicer(), server)
        
        main_server_address = config.read_server_address_from_config_file(config_path, 'main')
        
        server.add_insecure_port(main_server_address)
        server.start()
    except Exception as e:
        logging.critical(f"Main gRPC-server failed to start -> {e}")
        raise
    
    logging.info(f"Main gRPC-server is running on {main_server_address}")
    print(f"Main gRPC-server is running on {main_server_address}\n")
    
    try:
        while True:
            time.sleep(86400)  # Keep server active one day
    except KeyboardInterrupt:
        logging.info("Main gRPC-server is shuting down.")
        print("Main gRPC-server is shuting down.\n")
        server.stop(0) # Stops the server immediately when a KeyboardInterrupt is raised (e.g., CTRL+C)

"""
    Connects to the local modem gRPC server
    
    :param : None
    :return: None
"""
def use_MODEM():
    try:
        logging.info("Main gRPC-client trying to connect with Modem gRPC-server...")
        global stub, channel
        
        modem_server_address = config.read_server_address_from_config_file(config_path, 'modem')
        
        channel = grpc.insecure_channel(modem_server_address)
        stub    = modemCommunication_pb2_grpc.ModemCommunicationServiceStub(channel)
        logging.info(f"Main gRPC-client connected to the Modem gRPC-server running on {modem_server_address}.")
        
    except Exception as e:
        logging.critical(f"Main gRPC-client failed to connect with Modem gRPC-server: {e}")
        raise


use_MODEM()
serve_ADC()


"""
def test():
    
    global stub, channel
    
    logging.info("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.")
    print("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.\n")
            
    request_for_modem   = modemCommunication_pb2.ModemCommunicationRequest(message="Object Detected",contact_number=config_data.read_contact_number_from_config_file(config_path))
    reply_from_modem    = stub.ModemCommunication(request_for_modem)
            
    logging.info(f"Main gRPC-client received gRPC-reply from modem gRPC-server: {reply_from_modem.message}")
    print(f"Main gRPC-client received gRPC-reply from modem gRPC-server: {reply_from_modem.message}\n")
    
"""    
