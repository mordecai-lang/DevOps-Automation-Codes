from utilis import run_cmd
from logger import get_logger
import json
import subprocess
import os

log = get_logger()

DEPLOY_USER = "deployUserTest"
GROUP       = "developers"
SERVER_PIP  = "192.168.80.129"

def checkUser(username):
    cmd = ["grep", "-q", f"^{username}:", "/etc/passwd"]
    result = run_cmd(cmd,check=False, return_result=True)
    if result.returncode == 0:
        log.info("User %s exists", username)
        return True

    elif result.returncode == 1:
        log.info("User %s does not exist", username)
        return False

    else:
        log.error("Failed to check user %s: %s", username, result.stderr)
        raise RuntimeError(f"Unable to check user {username}")

#creating user with home directory
def createLinuxUser(username, shell):
    cmd = ["sudo","useradd","-d" ,f"/home/{username}", "-s", shell ,"-m", username]

    try:
        result = run_cmd(cmd)
        log.info(f"User {username} created successfully")
        return result
    except Exception:
        log.error(f"Unable to create user {username}")
        raise


#check if group exists
def checkGroup(group):
  cmd    = ["grep", f"^{group}:", "/etc/group"]
  try:
    result = run_cmd(cmd)
    return True
  except Exception as e:
    log.error(f"Unable to check group {group}")
    return False


def createGroup(group):
  cmd = ["sudo","groupadd", group]
  try:
    result = run_cmd(cmd)
    log.info(f"Group {group} created Successfully") 
    return result
  except Exception as e:
    log.error(f"Unable to create group {group}")
    raise

def addUserToGroup(group,username):
  cmd = ["sudo","usermod", "-aG", group, username]
  try:
    result = run_cmd(cmd)
    log.info(f"User {username} added to {group} group")
    return result
  except Exception as e:
    log.error(f"Unable to add {username} to {group} group")
    raise

def prepareSshDirectory(username):
    """
    Prepare the user's SSH directory so SSH public-key
    authentication can work.
    """

    ssh_directory = f"/home/{username}/.ssh"
    authorized_keys = f"{ssh_directory}/authorized_keys"

    # Create .ssh directory with permissions 700.
    # The user must own this directory.
    cmd = [
        "sudo", "install",
        "-d",
        "-m", "700",
        "-o", username,
        "-g", username,
        ssh_directory
    ]

    run_cmd(cmd)

    # Create authorized_keys if it does not exist.
    # touch does not erase existing keys.
    run_cmd(["sudo", "touch", authorized_keys])

    # Set ownership to the new user.
    run_cmd([
        "sudo", "chown",
        f"{username}:{username}",
        authorized_keys
    ])

    # Allow only the owner to read and write the file.
    run_cmd(["sudo", "chmod", "600", authorized_keys])

    log.info("SSH directory prepared for %s", username)

def generateSshKey():
  home = os.path.expanduser("~")
  key_path = home + "/.ssh/id_users"
  public_key_path = home + "/.ssh/id_users.pub"
  if os.path.exists(key_path) or os.path.exists(public_key_path):
    log.info("SSH key already exists. Skipping generation.")
    return

  cmd = ["ssh-keygen","-t", "rsa", "-b", "3072","-f", key_path,"-N", ""]
  try:
    result = run_cmd(cmd)
    log.info("SSH key generated locally at ~/.ssh/id_users")
    return result
  except Exception as e:
    log.error("Unable to generate ssh key")
    raise


def lockLinuxPassword(username):
    cmd = ["sudo", "passwd", "-l", username]
    run_cmd(cmd)
    log.info("Password locked for %s", username)


def copysshKeyToUser(username):
    home = os.path.expanduser("~")
    public_key_path = home + "/.ssh/id_users.pub"
    authorized_keys = f"/home/{username}/.ssh/authorized_keys"

    try:
        # Append the locally generated public key.
        run_cmd(["sudo", "sh", "-c",f"cat '{public_key_path}' >> '{authorized_keys}'"])

        # Set correct ownership and permissions.
        run_cmd(["sudo", "chown",f"{username}:{username}",authorized_keys])
        run_cmd(["sudo", "chmod", "600", authorized_keys])
        
        log.info("SSH public key installed for %s", username)

    except Exception:
        log.exception("Unable to install SSH public key for %s", username)
        raise



def testSSHConnection(username, server_ip):
  home = os.path.expanduser("~")
  key_path = home + "/.ssh/id_users"
  cmd = ["ssh","-i", key_path,"-o", "BatchMode=yes","-o", "PreferredAuthentications=publickey","-o", "ConnectTimeout=10",f"{username}@{server_ip}","exit"]

  try:
    result = run_cmd(cmd)
    log.info(f"SSH connection to {username}@{server_ip} was successful")
    return result
  except Exception as e:
    log.error(f"Unable to establish SSH connection to {username}@{server_ip}")
    raise

def runSudoersSscript():
  cmd = ["chmod", "+x", "linux-sudoers.sh"] 
  second_cmd = ["./linux-sudoers.sh"]

  try:
    result = run_cmd(cmd)
    second_result = run_cmd(second_cmd)
    log.info("File was executed successfully")
    return result, second_result
  except Exception as e:
    log.error("Could not execute file") 
    raise

def main():
  #check if users already exists
  if checkUser(DEPLOY_USER):
    log.info(f"User {DEPLOY_USER} already exists")
  else:
    log.info(f"User {DEPLOY_USER} does not exist, creating user")
    createLinuxUser(DEPLOY_USER, "/bin/bash")

  #Create Group
  if checkGroup(GROUP):
    log.info(f"Group {GROUP} already exists")
  else:
    log.info(f"Group {GROUP} does not exist, creating group")
    createGroup(GROUP)

  #add users to Groups
  addUserToGroup(GROUP, DEPLOY_USER)

  #generate ssh keys
  generateSshKey()

  #prepare ssh directory
  prepareSshDirectory(DEPLOY_USER)

  #copy ssh keys to users server
  copysshKeyToUser(DEPLOY_USER)

  #test ssh connection to users server
  testSSHConnection(DEPLOY_USER,SERVER_PIP)

  #Lock the account password.
  lockLinuxPassword(DEPLOY_USER)

  #run sudoers script
  runSudoersSscript()

if __name__ == "__main__":
  main()
