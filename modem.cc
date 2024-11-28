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


using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

using modemCommunication::ModemCommunicationService;
using modemCommunication::ModemCommunicationReply;
using modemCommunication::ModemCommunicationRequest;

std::atomic<bool> server_running(true); // flag
// Create logger instance
Logger logger("modem.log");
// path to the config file in JSON format  
std::string config_path = "config_modem.json";                  


class ModemCommunicationServiceImpl final : public ModemCommunicationService::Service {
public:
    Status ModemCommunication(ServerContext* context, const ModemCommunicationRequest* request, ModemCommunicationReply* reply) override
    {
        logger.log(INFO, "Modem gRPC-server received gRPC-request from Main gRPC-client. Request message: "+request->message());
        
        // Send SMS to contact_number
        int32_t contact_number = request->contact_number();
        logger.log(INFO, "Sending SMS to " + std::to_string(contact_number));
        // Send SMS to contact_number
    
        std::string reply_for_main = "Modem gRPC-server took action. SMS send.";
        logger.log(INFO, "Modem gRPC-server sends gRPC-reply to Main gRPC-client. Reply message: "+reply_for_main);
        reply->set_message(reply_for_main);

        return Status::OK;
    }
};

void serve_main() {
    
    std::string   server_address;
    ServerBuilder builder;
    ModemCommunicationServiceImpl service;
    std::unique_ptr<Server> server;
    
    try{
    
        server_address = read_server_address_from_config_file(config_path, "modem_server_address");
        
        builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
        builder.RegisterService(&service);
        
        server = builder.BuildAndStart();
        
        if (!server) 
            throw std::runtime_error("Failed to start the Modem server.");

    }catch (std::exception& e) {
        logger.log(CRITICAL, std::string("Modem gRPC-server failed to start -> ") + e.what());
        throw; // propagation
    }
    
    logger.log(INFO, "Modem gRPC server is running on " + server_address);

    while (server_running) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    logger.log(INFO, "Modem gRPC server is shutting down.");
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
