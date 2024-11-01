# Kernel-Space Driver Development and gRPC-Based Communication for an Autonomous Vehicle Detection and Imaging System

I am developing a system that integrates an IR distance sensor with an ADC 12 click, emphasizing the creation of kernel-space drivers for both the ADC and a camera. <br>
The system detects a passing vehicle through the IR sensor and relays this information to a user-space application -> `main1.py`.<br> 
Upon receiving the signal, `main1.py` sends a gRPC message to another user-space application -> `main2.py`, which subsequently triggers the camera driver to capture the vehicle’s license plate. <br>
This project focuses on robustly implementing the ADC and camera drivers in kernel space, alongside building two user-space applications that communicate seamlessly using gRPC messaging.
