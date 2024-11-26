import grpc
import time
import logging
import config_data
import modemCommunication_pb2
import modemCommunication_pb2_grpc
import objectProximityDetectionService_pb2
import objectProximityDetectionService_pb2_grpc
from concurrent import futures

channel = None
stub    = None

# Configure logging
logging.basicConfig(filename='main.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
                    
config_path = "config.json"

class ObjectProximityDetectionServiceServicer(objectProximityDetectionService_pb2_grpc.ObjectProximityDetectionServiceServicer):
    def ObjectProximityDetection(self, request, context):
        
        global stub
        
        logging.info(f"Main gRPC-server received gRPC-request from ADC gRPC-client: request.message={request.message}, request.object_proximity_distance={request.object_proximity_distance}")
        print(f"Main gRPC-server received gRPC-request from ADC gRPC-client: request.message={request.message}, request.object_proximity_distance={request.object_proximity_distance}\n")
        
        ########## OBRADA #############
        
        #if request.object_proximity_distance > THRESHOLD1:
            # D-Bus komunikacija sa drajverom kamere
        
        if request.object_proximity_distance > THRESHOLD2:
            
            logging.info("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.")
            print("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.\n")
            
            request_for_modem   = modemCommunication_pb2.ModemCommunicationRequest(message="Object Detected",contact_number=read_contact_number_from_config_file(config_path))
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
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    objectProximityDetectionService_pb2_grpc.add_ObjectProximityDetectionServiceServicer_to_server(ObjectProximityDetectionServiceServicer(), server)
    server.add_insecure_port('127.0.0.1:50051') # Main gRPC server is running on port 50051
    server.start()
    
    logging.info("Main gRPC server is running on 127.0.0.1:50051.")
    print("Main gRPC server is running on 127.0.0.1:50051.\n")
    
    try:
        while True:
            time.sleep(86400)  # Keep server active
            
    except KeyboardInterrupt:
        logging.info("Main gRPC server is shuting down.")
        print("Main gRPC server is shuting down.\n")
        server.stop(0) # Stops the server immediately when a KeyboardInterrupt is raised (e.g., CTRL+C)

"""
    Connects to the local modem gRPC server
    
    :param : None
    :return: None
"""
def use_MODEM():
    global stub, channel
    
    channel = grpc.insecure_channel('127.0.0.1:50052')
    stub = modemCommunication_pb2_grpc.ModemCommunicationServiceStub(channel)

def test():
    
    global stub, channel
    
    logging.info("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.")
    print("Object Detected. Main gRPC-client sends gRPC-request to modem gRPC-server.\n")
            
    request_for_modem   = modemCommunication_pb2.ModemCommunicationRequest(message="Object Detected",contact_number=config_data.read_contact_number_from_config_file(config_path))
    reply_from_modem    = stub.ModemCommunication(request_for_modem)
            
    logging.info(f"Main gRPC-client received gRPC-reply from modem gRPC-server: {reply_from_modem.message}")
    print(f"Main gRPC-client received gRPC-reply from modem gRPC-server: {reply_from_modem.message}\n")
    
    

use_MODEM()
#serve_ADC()
test()
