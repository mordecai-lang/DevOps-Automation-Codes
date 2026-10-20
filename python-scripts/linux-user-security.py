from utilis import run_cmd
from logger import get_logger
import json
import subprocess

log = get_logger()

APP_USER    = "appuser"
DEPLOY_USER = "deploy"
GROUP       = "developers"

def checkUser(username):
  cmd    = ["grep", f"^{username}:", "/etc/passwd"]
  try:
    result = run_cmd(cmd)
    return True
  except Exception as e:
    log.error(f"Unable to check user {username}")
    return False

#creating user with home directory
def createLinuxUser(username, shell):
    cmd = ["useradd","--create-home","--home-dir", f"/home/{username}","--shell", shell,username]

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
  cmd = ["groupadd", group]
  try:
    result = run_cmd(cmd)
    log.info(f"Group {group} created Successfully") 
    return result
  except Exception as e:
    log.error(f"Unable to create group {group}")
    raise

def addUserToGroup(group,username):
  cmd = ["usermod", "-aG", group, username]
  try:
    result = run_cmd(cmd)
    log.info(f"User {username} added to {group} group")
    return result
  except Exception as e:
    log.error(f"Unable to add {username} to {group} group")
    raise

def copysshKeyToUser(username ,server_ip):
  cmd = ["scp", "~/.ssh/id_users.pub", f"{username}@{server_ip}:/home/{username}/.ssh/authorized_keys"]
  try:
    result = run_cmd(cmd)
    log.info(f"SSH Key copied to {username}")    
    return result
  except Exception as e:
    log.error(f"Unable to copy SSH Key to {username}")
    raise

def testSSHConnection(username, server_ip):
  cmd = ["ssh", f"{username}@{server_ip}"]
  try:
    result = run_cmd(cmd)
    log.info(f"SSH connection to {username}@{server_ip} successful")
    return result
  except Exception as e:
    log.error(f"Unable to establish SSH connection to {username}@{server_ip}")
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

  #copy ssh keys to users server
  copysshKeyToUser(APP_USER, "123.234.345.456")
  copysshKeyToUser(DEPLOY_USER, "123.234.345.456")

  #test ssh connection to users server
  testSSHConnection(APP_USER, "123.234.345.456")
  testSSHConnection(DEPLOY_USER, "123.234.345.456")

if __name__ == "__main__":
  main()    
