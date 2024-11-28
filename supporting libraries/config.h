#include <iostream>
#include <fstream>
#include <string>
#include <nlohmann/json.hpp> // JSON library

using json = nlohmann::json;

std::string read_server_address_from_config_file(const std::string& filePath, const std::string& server) {
    try {
        // Opens file
        std::ifstream file(filePath);
        // Checks if file is sucessfully opened
        if (!file.is_open())
            throw std::runtime_error("Unable to open file: " + filePath);

        // Parsing JSON
        json config;
        file >> config;

        if (config.contains(server) && config[server].is_string())
            return config[server].get<std::string>();
        else
            throw std::runtime_error("Key '" + server + "' not found or not a string in "+filePath);
    }catch(std::exception& e){
        throw;
    }
}
