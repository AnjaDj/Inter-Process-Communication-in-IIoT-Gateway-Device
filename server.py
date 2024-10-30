import grpc
import time
import camera
import logging
import service_pb2
import service_pb2_grpc
from datetime import datetime
from concurrent import futures

# Configure logging
logging.basicConfig(level=logging.INFO)

filepath = "/home/rpi/img"

class MotionDetectionServiceServicer(service_pb2_grpc.MotionDetectionServiceServicer):
    def MotionDetection(self, request, context):
        logging.info(f"Received request from Motion Detection client: {request.name}")
        print(f"Received request from Motion Detection client: {request.name}")
        
        filename = filepath + create_time_stamp() + ".jpg"
        try:
            camera.takePic(filename)
            reply_message = f"Taking action from server - photo {filename} taken -"
            logging.info(reply_message)
        except Exception as e:
            reply_message = f"Taking action from server - failed to take photo: {str(e)}"
            logging.error(reply_message)
        
        return service_pb2.MotionDetectionReply(message=reply_message)

# Running gRPC server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MotionDetectionServiceServicer_to_server(MotionDetectionServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Server is running on port 50051...")
    print("Server is running on port 50051...")
    
    try:
        while True:
            time.sleep(86400)  # Keep server active
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
        print("Shutting down server...")
        server.stop(0)

def create_time_stamp():
    now = datetime.now()	# current time
    timestamp = now.strftime("%Y%m%d%H%M%S") # Desired formating
    return timestamp

if __name__ == '__main__':
    serve()
