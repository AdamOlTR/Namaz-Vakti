#!/bin/bash

echo "Starting script..."

# Check if Python3 is installed, if not install it
if ! command -v python3 &> /dev/null
then
    echo "Python3 not found. Installing Python3..."
    sudo apt-get update
    sudo apt-get install -y python3
else
    echo "Python3 is already installed."
fi

# Check if Chromium is installed, if not install it
if ! command -v chromium-browser &> /dev/null
then
    echo "Chromium not found. Installing Chromium..."
    sudo apt-get update
    sudo apt-get install -y chromium-browser
else
    echo "Chromium is already installed."
fi

# Check if xdotool is installed, if not install it
if ! command -v xdotool &> /dev/null
then
    echo "xdotool not found. Installing xdotool..."
    sudo apt-get update
    sudo apt-get install -y xdotool
else
    echo "xdotool is already installed."
fi

# Set DISPLAY variable to use the correct display
export DISPLAY=:0

echo "Disabling screensaver and power management..."
# Disable screensaver and power management
xset s noblank
xset s off
xset -dpms

# Fix Chromium crash issues
CHROMIUM_PREFS="/home/pi/.config/chromium/Default/Preferences"
if [ -f "$CHROMIUM_PREFS" ]; then
    echo "Fixing Chromium crash issues..."
    sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' "$CHROMIUM_PREFS"
    sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' "$CHROMIUM_PREFS"
else
    echo "Chromium preferences file not found. Skipping crash fix."
fi

# Start the Python script
echo "Starting the Python script..."
python3 /home/tugay/Namaz-Vakti/Namaz-Vakti/Main.py &
PYTHON_PID=$!

# Give some time for the Python script to start and generate the HTML file
echo "Waiting for the Python script to generate the HTML file..."
sleep 10

# Start Chromium in kiosk mode with the generated HTML file and additional flags for fullscreen and hiding the mouse cursor
echo "Starting Chromium in kiosk mode..."
/usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk --no-sandbox --ignore-certificate-errors --disable-web-security --user-data-dir=/home/tugay/chrome_data /home/tugay/Namaz-Vakti/Namaz-Vakti/namaz_times.html &

# Hide the mouse cursor after 0.1 seconds of inactivity
unclutter -idle 0.1 &

# Loop to switch tabs every 10 seconds (if multiple URLs are provided)
echo "Starting loop to switch tabs every 10 seconds..."
while true; do
    xdotool keydown ctrl+Tab
    xdotool keyup ctrl+Tab
    sleep 10
done

# Wait for Python script to finish (shouldn't normally happen with &)
wait $PYTHON_PID
echo "Python script finished."

echo "Script completed."

# Clear the terminal
clear
