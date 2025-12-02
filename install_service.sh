#!/usr/bin/env bash
# Install PhoenixV2 systemd service for auto-start and restart on failure
set -e

SERVICE_NAME="phoenix-v2"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
WORK_DIR="$(pwd)/PhoenixV2"
EXEC_CMD="/usr/bin/python3 ${WORK_DIR}/supervisor.py"

UNIT_FILE_CONTENT="[Unit]
Description=Phoenix V2 Trading Engine
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${WORK_DIR}
ExecStart=${EXEC_CMD}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"

if [ "$EUID" -ne 0 ]; then
  echo "This installer requires sudo. You will be prompted for your password."
  echo "Unit will be written to ${SERVICE_FILE} using sudo."
  echo "Unit content:"
  echo "${UNIT_FILE_CONTENT}"
  echo ""
  echo "Installing service..."
  printf "%s" "${UNIT_FILE_CONTENT}" | sudo tee ${SERVICE_FILE} > /dev/null
  sudo systemctl daemon-reload
  sudo systemctl enable ${SERVICE_NAME}
  echo "Service installed. Start it with: sudo systemctl start ${SERVICE_NAME}"
  exit 0

fi

echo "Writing unit to ${SERVICE_FILE}"
printf "%s" "${UNIT_FILE_CONTENT}" > ${SERVICE_FILE}
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
echo "Service installed. Start it with: sudo systemctl start ${SERVICE_NAME}"

