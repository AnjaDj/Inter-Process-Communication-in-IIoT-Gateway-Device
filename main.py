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

modem_server_address = None
threshold0           = None
threshold1           = None

def get_thresholds():
    
    global threshold0, threshold1
    
    try:
        threshold0 = config.get_config(config_path,'threshold0')
        threshold1 = config.get_config(config_path,'threshold1')
    except Exception as e:
        logging.critical(f"An error occurred while getting config data: {e}")
        raise

class ObjectProximityDetectionServiceServicer(objectProximityDetectionService_pb2_grpc.ObjectProximityDetectionServiceServicer):
    def ObjectProximityDetection(self, request, context):
        
        global stub, channel, threshold0, threshold1
        
        logging.info(f"Main gRPC-server received gRPC-request from ADC gRPC-client: Message={request.message}, distance={request.object_proximity_distance}")
        
        ########## OBRADA #############
        
        if request.object_proximity_distance > threshold0:
            logging.info("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.")
            
            number = config.get_config(config_path,'contact')
            
            request_for_modem   = modemCommunication_pb2.ModemCommunicationRequest(message="Object Detected",contact_number=number)
            reply_from_modem    = stub.ModemCommunication(request_for_modem)
            
            logging.info(f"Main gRPC-client received gRPC-reply from modem gRPC-server: {reply_from_modem.message}")
        
        elif request.object_proximity_distance > threshold1:
            logging.info("Object Detected. Main gRPC-client sends D-Bus message to Camera.")
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
        
        main_server_address = config.get_config(config_path, 'main')
        
        server.add_insecure_port(main_server_address)
        server.start()
        
        logging.info(f"Main gRPC-server is running on {main_server_address}")
    
    except grpc.RpcError as e:
        logging.critical(f"Failed to start main gRPC-server: grpc.RpcError: {e.code()} - {e.details()}")
        raise RuntimeError(f"Failed to start main gRPC-server: grpc.RpcError: {e}")
    except Exception as e:
        logging.critical(f"Main gRPC-server failed to start: {e}")
        raise
    
    try:
        while True:
            time.sleep(86400)  # Keep server active one day
    except KeyboardInterrupt:
        logging.info("Main gRPC-server is shuting down.")
        server.stop(0) # Stops the server immediately when a KeyboardInterrupt is raised (e.g., CTRL+C)

"""
    Connects to the local modem gRPC server
    
    :param max_retries: Retry the connection 
    :return: None
"""
def use_MODEM(max_retries=3):
    
    attempt = 1
    while attempt <= max_retries:
        try:
            global stub, channel, modem_server_address
            
            modem_server_address = config.get_config(config_path, 'modem')
            connection_time      = config.get_config(config_path, 'connection_time')
            
            logging.info(f"Main gRPC-client trying to connect with Modem gRPC-server running on {modem_server_address}")
            
            # Creates channel
            channel = grpc.insecure_channel(modem_server_address)
            # Checks if channel is ready for communication
            grpc.channel_ready_future(channel).result(timeout=connection_time)
            # Stub creating
            stub    = modemCommunication_pb2_grpc.ModemCommunicationServiceStub(channel)
            
            logging.info(f"Main gRPC-client connected to the Modem gRPC-server running on {modem_server_address}.")
            return
            
        except grpc.FutureTimeoutError:
            logging.error(f"Timeout limit exceeded. Main gRPC-client couldnt establish connection with Modem gRPC-server {modem_server_address}")
        except grpc.RpcError as e:
            logging.error(f"RPC error occurred at MAIN - MODEM line : {e.code()} - {e.details()}")
        except Exception as e:
            logging.error(f"Main gRPC-client failed to connect to the Modem gRPC-server running on {modem_server_address}: {e}")
            
        attempt += 1
        
        if attempt <= max_retries:
            logging.warning(f"Main Retrying to connect to the Modem gRPC-server running on {modem_server_address} in 3 seconds...")
            time.sleep(3)
        else:
            logging.critical(f"MAIN reached max connection retries. Unable to connect to the Modem gRPC-server running on {modem_server_address}  after multiple attempts")
            if 'channel' in globals() and channel is not None:
                channel.close()
            raise RuntimeError("Failed to connect to the Modem gRPC-server after multiple attempts.")

get_thresholds()
use_MODEM()
serve_ADC()
