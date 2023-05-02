import subprocess
import csv

# Function to run adb shell command and get the output
def run_adb_shell_command(command):
    cmd = ['adb', 'shell'] + command
    output = subprocess.check_output(cmd)
    return output.decode('utf-8')

# Check if the device is connected via USB
adb_devices_output = subprocess.check_output(['adb', 'devices']).decode('utf-8')
if 'unauthorized' in adb_devices_output:
    print("Please check the connected device and authorize this computer.")
    exit(1)
elif 'device' not in adb_devices_output:
    print("No device connected. Please connect your Android device via USB.")
    exit(1)

# Run the adb shell command and get the output
output_str = run_adb_shell_command(['content', 'query', '--uri', 'content://contacts/phones', '--projection', 'display_name:number'])

# Split the string into lines and remove any trailing newline characters
lines = [line.strip() for line in output_str.split('\n')]

# Create a list of dictionaries, where each dictionary represents a row in the output
rows = []
for line in lines:
    if line:
        name, number = line.split(',')
        name = name.split('=', 1)[-1].strip()
        number = number.split('=', 1)[-1].strip()
        rows.append({'display_name': name, 'number': number})

# Save the list of dictionaries to a CSV file
with open('contacts.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['display_name', 'number'])
    writer.writeheader()
    writer.writerows(rows)

print("Contacts have been saved to contacts.csv.")
