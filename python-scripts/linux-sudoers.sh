#!/bin/bash
set -euo pipefail
#create deploy script directory and file
sudo mkdir -p /usr/local/sbin
if [ ! -f /usr/local/sbin/deploy-myapp ]; then
  sudo touch /usr/local/sbin/deploy-myapp
fi

#set file script ownership and permission
sudo chown root:root /usr/local/sbin/deploy-myapp
sudo chmod 750 /usr/local/sbin/deploy-myapp

#set directory ownership with restricted others privileges to be implemented
sudo chown root:root /usr/local/sbin
sudo chmod 755 /usr/local/sbin

#add deploy user to sudoers restricting parsing argument
SUDOERS_FILE="/etc/sudoers.d/deploy-myapp"
TEMP_FILE=$(mktemp)

#make file delete after script is done
trap 'rm -f "$TEMP_FILE"' EXIT
#write the permitted command
printf '%s\n' 'deploy ALL=(root) NOPASSWD: /usr/local/sbin/deploy-myapp ""'  | sudo tee "$TEMP_FILE" >/dev/null

#set temporary file permission
sudo chmod 0440 "$TEMP_FILE"

#validate temporary file configuration
sudo visudo -cf "$TEMP_FILE"

#install config to main sudoers file
sudo install -o root -g root -m 0440 "$TEMP_FILE" "$SUDOERS_FILE"

#Validate
sudo visudo -c

echo "Deployment script permissions and sudoers rule configured."
