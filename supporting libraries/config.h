#include <iostream>
#include <fstream>
#include <string>
#include <nlohmann/json.hpp> // JSON library

using json = nlohmann::json;

std::string read_server_address_from_config_file(const std::string& filePath, const std::string& key) {
    try {
        // Opens file
        std::ifstream file(filePath);
        // Checks if file is sucessfully opened
        if (!file.is_open())
            throw std::runtime_error("Unable to open file: " + filePath);

        // Parsing JSON
        json config;
        file >> config;

        if (config.contains(key) && config[key].is_string())
            return config[key].get<std::string>();
        else
            throw std::runtime_error("Value error: '" + key + "' not found or is in wrong format in "+filePath);
    }catch(std::exception& e){
        throw;
    }
}
