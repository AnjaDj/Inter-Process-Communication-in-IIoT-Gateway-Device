# Kernel-Space Driver Development and gRPC-Based Communication for an Autonomous Vehicle Detection and Imaging System

I am developing a system that integrates an IR-distance-sensor with an ADC-12-click as input side, and camera at output side.  <br><br>

The system measures the distance between IR-distance-sensor and objects in front of it. Those analog values are sent to ADC. Converted values are sent to RPI via I2C communication interface.<br> 
client.py reads data from ADC and checks whether a nearby object has been detected and sends gRPC message if nearby object has been detected.<br><br>

server.py receives gRPC request and responds to it by taking a picture.<br> <br>

The client checks whether a nearby object has been detected and sends gRPC message if so. The server responds to gRPC request by taking a picture.
