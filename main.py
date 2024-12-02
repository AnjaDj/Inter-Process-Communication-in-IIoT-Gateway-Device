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
server  = None
stub    = None # connection to modem gRPC server

# Configure logging
logging.basicConfig(filename='main.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
                    
# path to the config file in JSON format                    
config_path = "config_main.json"

modem_server_address = None
main_server_address  = None
connection_time      = None
threshold0           = None
threshold1           = None
number               = None

def get_configs():
    global modem_server_address, main_server_address, threshold0, threshold1, connection_time, number
    
    try:
        modem_server_address = config.get_config(config_path, 'modem')
        main_server_address  = config.get_config(config_path, 'main')
        threshold0           = config.get_config(config_path, 'threshold0')
        threshold1           = config.get_config(config_path, 'threshold1')
        connection_time      = config.get_config(config_path, 'connection_time')
        number               = config.get_config(config_path, 'contact')
    except Exception as e:
        logging.critical(f"An error occurred while getting config data: {e}")
        raise

class ObjectProximityDetectionServiceServicer(objectProximityDetectionService_pb2_grpc.ObjectProximityDetectionServiceServicer):
    def ObjectProximityDetection(self, request, context):
        
        global stub, channel, threshold0, threshold1, number
        
        logging.info(f"Main server received request from ADC client: Message={request.message}, distance={request.object_proximity_distance}")
        
        ########## OBRADA #############
        if request.object_proximity_distance > threshold0:
            logging.info("Main client sends request to Modem server.")
            
            request_for_modem   = modemCommunication_pb2.ModemCommunicationRequest(message="Object Detected",contact_number=number)
            reply_from_modem    = stub.ModemCommunication(request_for_modem)
            
            logging.info(f"Main client received reply from Modem server: {reply_from_modem.message}")
        
        elif request.object_proximity_distance > threshold1:
            logging.info("Object Detected. Main client sends D-Bus message to Camera.")
        ########## OBRADA #############
        
        reply_for_ADC = "Main server took action."
        return objectProximityDetectionService_pb2.ObjectProximityDetectionReply(message=reply_for_ADC)
        

"""
    Sets up and runs a gRPC server for communication with ADC client
    
    :param max_retries: Max number of connection retries 
    :return: None
"""
def serve_ADC(max_retries=3):
    
    attempt = 1
    global main_server_address, server
    
    while attempt <= max_retries:
        try:
            logging.info(f"Starting Main server...")
            
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            objectProximityDetectionService_pb2_grpc.add_ObjectProximityDetectionServiceServicer_to_server(ObjectProximityDetectionServiceServicer(), server)
            
            server.add_insecure_port(main_server_address)
            server.start()
            
            logging.info(f"Main server is running on {main_server_address}")
            break
            
        except grpc.RpcError as e:
            logging.error(f"Main server failed to start: grpc.RpcError: {e.code()} - {e.details()}")
        except Exception as e:
            logging.error(f"Main server failed to start: {e}")
    
        attempt += 1
        
        if attempt <= max_retries:
            logging.warning(f"Main server retrying to start in 3 seconds...")
            time.sleep(3)
        else:
            logging.critical(f"Main reached max startup retries. Unable to start Main server after multiple attempts!")
            raise RuntimeError("Main server failed to start after multiple attempts.")
        
    try:
        while True:
            time.sleep(86400)  # Keep server active one day
    except KeyboardInterrupt:
        logging.info("Main server is shuting down.")
        server.stop(0) # Stops the server immediately when a KeyboardInterrupt is raised (e.g., CTRL+C)

"""
    Connects to the local modem gRPC server
    
    :param max_retries: Max number of connection retries 
    :return: None
"""
def use_MODEM(max_retries=3):
    
    attempt = 1
    global stub, channel, modem_server_address, connection_time
    
    while attempt <= max_retries:
        try:
            logging.info(f"Main client trying to connect to the Modem server...")
                  
            # Creates channel
            channel = grpc.insecure_channel(modem_server_address)
            # Checks if channel is ready for communication
            grpc.channel_ready_future(channel).result(timeout=connection_time)
            # Stub creating
            stub    = modemCommunication_pb2_grpc.ModemCommunicationServiceStub(channel)
            
            logging.info(f"Main client connected to the Modem server running on {modem_server_address}.")
            return
            
        except grpc.FutureTimeoutError:
            logging.error(f"Timeout limit exceeded. Main client couldnt establish connection with Modem server {modem_server_address}")
        except grpc.RpcError as e:
            logging.error(f"RPC error occurred at MAIN - MODEM line : {e.code()} - {e.details()}")
        except Exception as e:
            logging.error(f"Main client failed to connect to the Modem server running on {modem_server_address}: {e}")
            
        attempt += 1
        
        if attempt <= max_retries:
            logging.warning(f"Main Retrying to connect to the Modem server running on {modem_server_address} in 3 seconds...")
            time.sleep(3)
        else:
            logging.critical(f"MAIN reached max connection retries. Unable to connect to the Modem server running on {modem_server_address}  after multiple attempts")
            if 'channel' in globals() and channel is not None:
                channel.close()
            raise RuntimeError("Failed to connect to the Modem server after multiple attempts.")

get_configs()
use_MODEM()
serve_ADC()
