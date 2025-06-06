#!/bin/bash

# Configuration - Change these if needed
APP_DIR="/root/dental_clinic/dental_lab"
MAIN_PY="app.py"
VENV_PATH="$APP_DIR/venv/bin/python"
LOG_FILE="$APP_DIR/flask.log"

echo "?? Deploying Dental Clinic App..."

# Step 1: Find and kill only the correct Flask process
echo "?? Stopping existing Flask process..."
PIDS=$(ps aux | awk '/[p]ython.*app\.py/ && !/grep/ {print $2}')

if [ ! -z "$PIDS" ]; then
    echo "mPid(s):"
    echo "$PIDS"

    for PID in $PIDS; do
        echo "Killing PID: $PID"
        kill -9 $PID
    done

    echo "? Old process(es) killed."
else
    echo "?? No matching running process found."
fi

# Step 2: Navigate to project directory
cd "$APP_DIR" || { echo "? Failed to enter directory $APP_DIR"; exit 1; }

# Step 3: Start the app in background using nohup
echo "?? Starting Flask app with nohup..."
nohup "$VENV_PATH" "$MAIN_PY" > "$LOG_FILE" 2>&1 &

# Step 4: Wait and verify it started
sleep 3

NEW_PID=$(ps aux | awk '/[p]ython.*app\.py/ && !/grep/ {print $2}')
if [ ! -z "$NEW_PID" ]; then
    echo "? Deployment successful!"
    echo "mPid: $NEW_PID"
    echo "?? Logs: tail -f $LOG_FILE"
else
    echo "? Deployment failed. Check logs: cat $LOG_FILE"
fi