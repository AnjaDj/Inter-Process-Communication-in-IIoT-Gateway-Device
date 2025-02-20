# 🔸 Flash ARM image to SD Card<br>
Our Raspberry Pi (using RPi 3B) needs an operating system to work. There are a range of operating systems provided by Raspberry Pi.<br>
We can use <b>Raspberry Pi Imager</b> as the quick and easy way to install an operating system to a microSD card, or
alternatively, we can choose from many operating systems available, download it and install manually.<br>
From `https://www.raspberrypi.com/software/operating-systems/` Raspberry Pi OS (64-bit) is downloaded.
![image](https://github.com/user-attachments/assets/b13ee226-5e6b-44b8-8ada-3bafec3314a4)<br>

After the download is complited, the `2024-11-19-raspios-bookworm-arm64.img.xz` file should be placed in Download dir of our PC.<br>
1. Insert the SD card into the memory card slot and use the command `lsblk` to list block devices such as SD cards, HDD, etc.<br>
    Your SD card is most likely recognized as<br>
    sdb                        8:16   1  29,1G   0 disk<br>
      ├─sdb1                  8:17   1   128M  0 part  /media/user/BOOT<br>
      └─sdb2                  8:18   1    29G   0 part  /media/user/rootfs<br>
      
2. Unmount the SD card to be able to write to it.(If your SD card is device /dev/sdb having two partitions, do below to unmount them)
   ```bash
   umount /dev/sdb1
   umount /dev/sdb2
   
3. Flash ARM image to SD Card:
   ```bash
   xzcat /path/to/2024-11-19-raspios-bookworm-arm64.img.xz | sudo dd bs=1M of=/dev/sdb

4. Now 64bit RPi OS is flashed to your SD card. Eject it from PC and insert it into RPi 3B device.



# 🔸 Natively build a Linux kernel on RPi 3B<br>
Complete quidance on : https://www.raspberrypi.com/documentation/computers/linux_kernel.html#install-directly-onto-the-sd-card.<br>
This guide assumes that your Raspberry Pi runs the latest version of Raspberry Pi OS. <br>
  `sudo apt install git`<br>
  `git clone --depth=1 https://github.com/raspberrypi/linux`

1. Install the build dependencies <br>
   `sudo apt install bc bison flex libssl-dev make`
2. Build configuration<br>
   In this case, Im using RPi3B and for 32bit distribution run following commands
   ```bash
   cd linux
   KERNEL=kernel7
   make bcm2709_defconfig
3. Build the 32-bit kernel (this step will take A LONG TIME -couple of hours)<br>
   `make -j6 zImage modules dtbs`
4. Install the kernel modules onto the boot media<br>
   `sudo make -j6 modules_install`
5. Create a backup of your current kernel and install the fresh kernel image
   ```bash
   sudo cp /boot/firmware/$KERNEL.img /boot/firmware/$KERNEL-backup.img
   sudo cp arch/arm/boot/zImage /boot/firmware/$KERNEL.img
6. For kernels version 6.5 and above<br>
   `sudo cp arch/arm/boot/dts/broadcom/*.dtb /boot/firmware/`
7. Copy over the overlays and README
   ```bash
   sudo cp arch/arm/boot/dts/overlays/*.dtb* /boot/firmware/overlays/
   sudo cp arch/arm/boot/dts/overlays/README /boot/firmware/overlays/
8. Finally, run the following command to reboot your Raspberry Pi and run your freshly-compiled kernel `sudo reboot`

   
# 🔸 gRPC
## Build and locally install gRPC and Protocol Buffers for C++ on Ubuntu x86_64 6.8.0-49-generic
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

## Build and locally install gRPC and Protocol Buffers for Python on Ubuntu x86_64 6.8.0-49-generic
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



# 🔸 From Python script to Linux service using <b>systemd</b>
A daemon (or service) is a background process that is designed to run autonomously,with little or not user intervention. Services will start automatically every time the system starts, which eliminates the need to start it manually. Scripts that collect data, represent servers or similar are ideal candidates to be configured as services and not ordinary scripts.<br>
  
1. Write Python script you want to make as service `/path/to/your_script.py`
2. Make your Python script executable
   ```bash
   ~$ chmod +x /path/to/your_script.py
4. Create systemd service file in directory `/etc/systemd/system/`.  Systemd service files need to be in `/etc/systemd/system/` DIR!
   ```bash
   ~$ sudo nano /etc/systemd/system/your_script.service
5. Add following content to your .service file
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

6. Reload systemd to recognise new service `your_script.service`
   ```bash
   sudo systemctl daemon-reload
8. Enable new service at system startup
   ```bash
   sudo systemctl enable your_script.service
10. Run service
    ```bash
    sudo systemctl start your_script.service
11. Managing the service
    - stop service
      ```bash
      sudo systemctl stop your_script.service
    - restart service
      ```bash
      sudo systemctl stop your_script.service
    - disable service at system startup
      ```bash
      sudo systemctl disable your_script.service
