import sys, re, subprocess

def warning_msg(id):
    def help_msg():
        print("\n\tUsage:\tpython3 sniffer.py <frequency>")
        print("\t\t<frequency>: MHz\n")

    if id == 1:
        help_msg()
    elif id == 2:
        print("Invalid channel frequency.")
        help_msg()
    sys.exit(1)


def check_interface_mode(interface):
    try:
        result = subprocess.run(['iwconfig', interface], capture_output=True, text=True, check=True)
        output = result.stdout
        
        if re.search(r'Mode:Monitor', output):
            return 0
        else:
            return 1
    except subprocess.CalledProcessError:
        return 2


def start_airmon_ng(interface, channel):
    try:
        print(f"\nStarting airmon-ng ...")
        subprocess.run(["airmon-ng", "start", interface, str(channel)], check=True)
        print(f"airmon-ng started successfully on frequency: {channel} MHz\n")
    except:
        print(f"Failed to start airmon-ng\n")

def stop_airmon_ng(interface):
    try:
        print(f"\nStoping airmon-ng ...")
        subprocess.run(["airmon-ng", "stop", interface], check=True)
        print(f"airmon-ng stopped successfully.\n")
    except:
        print(f"Failed to stop airmon-ng\n")


if __name__ == "__main__":
    wifi_interface = "wlp1s0"
    wifi_monitor = wifi_interface + "mon"

    if len(sys.argv) != 2:
        warning_msg(1)

    try:
        channel = int(sys.argv[1])
    except:
        warning_msg(2)

    status = check_interface_mode(wifi_monitor)

    if status == 0:
        stop_airmon_ng(wifi_monitor)
        start_airmon_ng(wifi_interface, channel)
    else:
        start_airmon_ng(wifi_interface, channel)

