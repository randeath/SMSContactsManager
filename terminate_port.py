import psutil
import os

def terminate_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print(f"Terminating process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}")
                    proc.terminate()
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

if __name__ == '__main__':
    terminate_process_on_port(8000)