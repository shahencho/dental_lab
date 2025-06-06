#!/bin/bash

# Configuration - Change these if needed
APP_DIR="/root/dental_clinic/dental_lab"
MAIN_PY="app.py"
APP_PATH="$APP_DIR/$MAIN_PY"
VENV_PATH="$APP_DIR/venv/bin/python"
LOG_FILE="$APP_DIR/flask.log"

echo "🚀 Deploying Dental Clinic App..."

# Step 1: Find and kill only the correct Flask process
echo "🛑 Stopping existing Flask process..."
PID=$(ps aux | awk -v app="$APP_PATH" '$0 ~ app && !/grep/ && /python/ {print $2}')

if [ ! -z "$PID" ]; then
    echo "mPid: $PID"
    kill -9 $PID
    echo "✅ Old process killed."
else
    echo "ℹ️ No matching running process found."
fi

# Step 2: Navigate to project directory
cd "$APP_DIR" || { echo "❌ Failed to enter directory $APP_DIR"; exit 1; }

# Step 3 (Optional): Pull latest changes from Git
#echo "🔄 Pulling latest code from Git (if applicable)..."
#git pull origin main || echo "⚠️ Git pull failed or not configured."

# Step 4: Start the app in background using nohup
echo "🟢 Starting Flask app with nohup..."
nohup "$VENV_PATH" "$MAIN_PY" > "$LOG_FILE" 2>&1 &

# Step 5: Verify it started
sleep 2
NEW_PID=$(ps aux | awk -v app="$APP_PATH" '$0 ~ app && !/grep/ && /python/ {print $2}')
if [ ! -z "$NEW_PID" ]; then
    echo "✅ Deployment successful!"
    echo "mPid: $NEW_PID"
    echo "📄 Logs: tail -f $LOG_FILE"
else
    echo "❌ Deployment failed. Check logs: cat $LOG_FILE"
fi