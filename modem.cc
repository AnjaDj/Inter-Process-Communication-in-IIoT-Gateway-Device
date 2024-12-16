#include <iostream>
#include <string>
#include <memory>
#include <csignal> 
#include <atomic>
#include <grpcpp/grpcpp.h>
#include "logger.h"
#include "config.h"
#include "modemCommunication.grpc.pb.h"
#include <chrono>   
#include <thread>    
#include <unistd.h>


using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

using modemCommunication::ModemCommunicationService;
using modemCommunication::ModemCommunicationReply;
using modemCommunication::ModemCommunicationRequest;

std::atomic<bool> server_running(true); // flag

Logger logger("modem.log");

// path to the config file in JSON format  
std::string config_path = "config_modem.json";                  


class ModemCommunicationServiceImpl final : public ModemCommunicationService::Service {
public:
    Status ModemCommunication(ServerContext* context, const ModemCommunicationRequest* request, ModemCommunicationReply* reply) override
    {
        logger.log(INFO, "Modem server received gRPC-request from Main client. Request message: "+request->message());
        
        // Send SMS to contact_number
        int32_t contact_number = request->contact_number();
        logger.log(INFO, "Sending SMS to " + std::to_string(contact_number));
        // Send SMS to contact_number
    
        std::string reply_for_main = "Modem server took action. SMS sent to " + std::to_string(contact_number);
        logger.log(INFO, "Modem server sends gRPC-reply to Main client. Reply message: "+reply_for_main);
        reply->set_message(reply_for_main);

        return Status::OK;
    }
};

void serve_main(int max_retries=3) {
    
    std::string   server_address;
    ServerBuilder builder;
    ModemCommunicationServiceImpl service;
    std::unique_ptr<Server> server;
    
    int attempt = 1;
    
    while(attempt <= max_retries){
        try{
        
            server_address = read_server_address_from_config_file(config_path, "modem_server_address");
            
            builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
            builder.RegisterService(&service);
            
            server = builder.BuildAndStart();
            
            if (!server) 
                throw std::runtime_error("Modem server failed to start");
            
            logger.log(INFO, "Modem server is running on " + server_address);
            break;

        }catch (std::exception& e) {
            logger.log(ERROR, "Modem server failed to start -> " + std::string(e.what()) );
        }
        
        attempt++;
        
        if (attempt <= max_retries){
            logger.log(WARNING, "Modem server retrying to start in 3 seconds...");
            sleep(3);
        }
        else{
            logger.log(CRITICAL, "Modem server reached max startup retries. Unable to start Modem server after multiple attempts!");
            throw std::runtime_error("Modem server failed to start after multiple attempts.");
        }
    }

    while (server_running)
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
    logger.log(INFO, "Modem server is shutting down.");
    server->Shutdown();
}

// Signal handler for SIGINT (CTRL+C)
void SignalHandler(int signal) {
    std::cout << "\nReceived command to shutdown the Modem gRPC-server - " << signal << ". Stopping the Modem server..." << std::endl;
    server_running = false;
}

int main(int argc, char** argv) {
    
    std::signal(SIGINT, SignalHandler);
    serve_main();
    
    return 0;
}
