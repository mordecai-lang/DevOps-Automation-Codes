<<<<<<< HEAD
set -e
# Create group
echo "[INFO] Creating group 'developers'"
sudo groupadd developers 

#verify group creation
echo "[INFO] Verifying group creation"
getent group developers
cut -d: -f1 /etc/group | grep developers

#create user with interactive shell
echo "[INFO] Creating user 'mordecai'"
sudo useradd -s /bin/bash -d /var/www/mordecai -m mordecai

#verify user creation
echo "[INFO] Verifying user creation"
getent passwd mordecai
cut -d: -f1 /etc/passwd | grep mordecai

# Add user to group
echo "[INFO] Adding user 'mordecai' to group 'developers'"
sudo usermod -aG developers mordecai

#give user and group permisions to the directory
echo "[INFO] Changing ownership of /var/www/mordecai to user 'mordecai' and group 'developers'"
sudo chown -R mordecai:developers /var/www/mordecai

#add user to docker group
echo "[INFO] Adding user 'mordecai' to group 'docker'"
sudo usermod -aG docker mordecai

#verify user is in group
echo "[INFO] Verifying user is in groups"
groups mordecai

# Make group own the directory
echo "[INFO] Changing ownership of /var/www/mordecai to user 'mordecai' and group 'developers'"
sudo chown mordecai:developers /var/www/mordecai

# Give owner rwx, group r-x, others nothing
echo "[INFO] Setting permissions for /var/www/mordecai]"
sudo chmod 750 /var/www/mordecai
=======
>>>>>>> fc7ad04 (First Push)
