# gRPC
## Build and locally install gRPC and Protocol Buffers for C++
Prerequisites<br>
 - cmake 3.16 or later (https://vitux.com/how-to-install-cmake-on-ubuntu/)
1. Configures a directory for locally installed packages and ensures the executables are easily accessible from the command line<br>
    ```bash
     ~$ export LOCAL_INSTALL_DIR=$HOME/.local
     ~$ mkdir -p $LOCAL_INSTALL_DIR
     ~$ export PATH="$LOCAL_INSTALL_DIR/bin:$PATH"
2. Install the basic tools required to build gRPC
     ```bash
     ~$ sudo apt install -y build-essential autoconf libtool pkg-config
3. Clone the grpc repo and its submodules
     ```bash
     ~$ git clone --recurse-submodules -b v1.66.0 --depth 1 --shallow-submodules https://github.com/grpc/grpc
4. Build and locally install gRPC and Protocol Buffers
     ```bash
     ~$ cd grpc
     ~/grpc$ mkdir -p cmake/build
     ~/grpc$ pushd cmake/build
     ~grpc/cmake/build$ cmake -DgRPC_INSTALL=ON \
                              -DgRPC_BUILD_TESTS=OFF \
                              -DCMAKE_INSTALL_PREFIX=$LOCAL_INSTALL_DIR \
                              ../..
     ~grpc/cmake/build$ make -j 4
     ~grpc/cmake/build$ make install
     ~grpc/cmake/build$ popd
5. Build the project<br>
    in `~/grpc/examples/protos/` save .proto file<br>
    in `~/grpc/examples/cpp/` create new directory `myproject` containing source .cc code and CMakeLists.txt<br>
    ```bash
    ~/grpc$ cd examples/cpp/myproject
    ~/grpc/examples/cpp/myproject$ mkdir -p cmake/build
    ~/grpc/examples/cpp/myproject$ pushd cmake/build
    ~/grpc/examples/cpp/myproject/cmake/build$ cmake -DCMAKE_PREFIX_PATH=$LOCAL_INSTALL_DIR ../..
    ~/grpc/examples/cpp/myproject/cmake/build$ make -j 4
6. Run the project from the project `build` directory<br>
    ```bash
    ~/grpc/examples/cpp/myproject/cmake/build$ ./app

## Build and locally install gRPC and Protocol Buffers for Python
Prerequisites<br>
 - Python 3.7 or higher
 - pip version 9.0.1 or higher

1. Install gRPC
   ```bash
   ~$ python3 -m pip install grpcio
2. Install gRPC tools
   ```bash
   ~$ python3 -m pip install grpcio-tools
3. Build the project<br>
   create new directory `myproject` containing .proto file and source .py code<br>
5. Run the project<br>
   from project directory `myproject` in terminal run `python3 app.py`



# From Python script to Linux service using <b>systemd</b>
Automatic starting and managing script as Linux service
  
1. Write Python script `/path/to/your_script.py`
2. Make script executable
   ```bash
   chmod +x /path/to/your_script.py
4. Create systemd service file in directory `/etc/systemd/system/`
   ```bash
   sudo nano /etc/systemd/system/your_script.service
5. Add following content to the .service file
   ```bash
   [Unit]
   Description=Python Script Service
   After=network.target
   
   [Service]
   ExecStart=/usr/bin/python3 /path/to/your_script.py
   Restart=always
   User=your_user
   WorkingDirectory=/path/to/
   Environment="PATH=/usr/bin"
   
   [Install]
   WantedBy=multi-user.target

6. Reload systemd to recognise new service
   ```bash
   sudo systemctl daemon-reload
8. Enable new service at system startup
   ```bash
   sudo systemctl enable your_script.service
10. Run service
    ```bash
    sudo systemctl start your_script.service
