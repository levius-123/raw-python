#!/bin/bash

# Run both Python scripts in the background
source venv/bin/activate &
python3 /home/user/YOUR_DIRECTORY/press3.html.py &
python3 /home/user/YOUR_DIRECOTRY/raw.html.py &
sudo rm /mnt/konvert/* &
##########################################################

# Wait for both processes to finish
#wait

