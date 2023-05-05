import subprocess
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

def load_private_key(file_path):
    with open(file_path) as f:
        priv = f.read()
    return priv

def create_signer(private_key):
    signer = PythonRSASigner('', private_key)
    return signer

def connect_device_wifi(adb_host, adb_port, signer):
    device = AdbDeviceTcp(adb_host, adb_port)
    device.connect(rsa_keys=[signer])
    return device

def run_adb_shell_command(command):
    cmd = ['adb', 'shell'] + command
    output = subprocess.check_output(cmd)
    return output.decode('utf-8')
