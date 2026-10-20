
import subprocess
import json
from logger import get_logger

log = get_logger()

def run_cmd(cmd: list, parse_json: bool = False, timeout: int = 60):
    try:
        result = subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=timeout)

        #convert JSON text output to python Dictionary or list
        if parse_json:
            return json.loads(result.stdout)
        return result.stdout

    #LOG disply for errors
    except subprocess.CalledProcessError as e:
        log.error(f"Command failed: {' '.join(cmd)}")
        log.error(e.stderr)
        raise

    #log display for timeout
    except subprocess.TimeoutExpired:
        log.error(f"Command timed out: {' '.join(cmd)}")
        raise

    #Log display for Invalid output json format
    except json.JSONDecodeError:
        log.error(f"Command returned invalid JSON: {' '.join(cmd)}")
        raise

    #log for non bash command
    except FileNotFoundError:
        log.error(f"Command not found: {cmd[0]}")
        raise
