import os
import subprocess

pid = 0

def takePic(filename):
    global pid
    pid = os.fork()
    
    if pid == 0:
        # Redirecting stdout and stderr into /dev/null
        with open(os.devnull, 'w') as devnull:
            os.dup2(devnull.fileno(), 1)  # Redirect stdout
            os.dup2(devnull.fileno(), 2)  # Redirect stderr
            
            # Execute the command
            os.execl("/usr/bin/rpicam-still",
                      "/usr/bin/rpicam-still",
                      "-n",
                      "-o",
                      filename)
            os._exit(1)  # Exit with error if execl fails

    elif pid > 0:
        # Wait for the child process to finish
        os.waitpid(pid, 0)
    else:
        # If fork fails
        print("Fork failed", file=os.stderr)

