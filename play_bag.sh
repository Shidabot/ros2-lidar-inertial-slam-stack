#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <rosbag-directory>" >&2
  exit 1
fi

ros2 bag play "$1"
