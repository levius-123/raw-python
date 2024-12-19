#!/bin/bash

# Run both Python scripts in the background
source venv/bin/activate &
python3 /home/doma/Dokumenty/KOMPRESS/press3.html.py &
python3 /home/doma/Dokumenty/KOMPRESS/raw.html.py &
sudo rm /mnt/konvert/* &
##########################################################
#python3 /home/doma/Dokumenty/VIDEA/video.test9.html.py &

# Wait for both processes to finish
#wait

