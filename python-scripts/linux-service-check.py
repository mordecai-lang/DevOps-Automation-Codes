
import subprocess
import logging

# Services we want to monitor
services = ["ssh", "docker", "nginx"]

# Record activity in a log file
logging.basicConfig(
    filename="service_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_service_status(service):
    """Return the current systemd service status."""

    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True,
        check=False
    )

    return result.stdout.strip()


for service in services:
    status = get_service_status(service)

    if status == "active":
        print(f"[OK] {service} is running")
        logging.info("%s is active", service)

    else:
        print(f"[WARNING] {service} is {status or 'unknown'}")
        logging.warning("%s is %s", service, status or "unknown")

        # Ask before attempting a restart
        approval = input(
            f"Do you want to restart {service}? (yes/no): "
        ).strip().lower()

        if approval == "yes":
            restart = subprocess.run(
                ["sudo", "systemctl", "restart", service],
                check=False
            )

            if restart.returncode == 0:
                print(f"[ACTION] Restart command succeeded for {service}")
                logging.info("Restart command succeeded for %s", service)
            else:
                print(f"[ERROR] Could not restart {service}")
                logging.error("Restart failed for %s", service)
        else:
            print(f"[SKIPPED] No restart for {service}")













import subprocess
import platform

# Servers we want to monitor
servers = [
    "8.8.8.8",          # Google DNS
    "1.1.1.1",          # Cloudflare DNS
    "192.168.1.10",     # Example internal server
    "192.168.1.20",     # Example internal server
    "10.0.0.5"          # Example private network server
]

# Detect the operating system
system = platform.system().lower()

# Select the correct ping arguments
if system == "windows":
    ping_args = ["-n", "1", "-w", "2000"]
else:
    ping_args = ["-c", "1", "-W", "2"]

print("SERVER REACHABILITY REPORT")
print("-" * 35)

for server in servers:
    try:
        result = subprocess.run(
            ["ping"] + ping_args + [server],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=4,
            check=False
        )

        if result.returncode == 0:
            print(f"[ONLINE]  {server} is reachable")
        else:
            print(f"[OFFLINE] {server} did not respond to ping")

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {server} took too long")

    except FileNotFoundError:
        print("Error: ping command was not found.")
        break
