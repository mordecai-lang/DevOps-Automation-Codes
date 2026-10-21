#!/bin/bash
set -eu

#check if command running script is of 0 arguments
if [ "$#" -ne 0 ]; then
    echo "This script accepts no arguments." >&2
    exit 2
fi

IMAGE     = "myapp:latest"
CONTAINER = "myapp_container"

#pull and run container
/usr/bin/docker pull "$IMAGE"
/usr/bin/docker rm -f "$CONTAINER" 2>/dev/null || true
/user/bin/docker run  -d --name "$CONTAINER" --restart unless-stopped -p 8080:8080 --user 10001:10001 --security-opt no-new-privileges:true "$IMAGE"
 
