# Audio Splitter
Description
The Audio Splitter is a Python-based tool that allows you to record audio and automatically split it into multiple segments based on keystrokes detected during the recording process. The program uses a combination of audio amplitude detection and keyboard input events to segment the audio and save it into individual .wav files.

This tool is ideal for applications where audio needs to be split around specific user interactions, such as transcription, lecture recordings, or podcasts.

# Features
Records audio in real-time.

Detects keystrokes based on audio amplitude spikes.

Automatically splits the audio file at detected keystrokes.

Saves split audio segments into .wav files.

Logs actual keystrokes (if desired) in a JSON file.

# Requirements
Python 3.x

pyaudio library for audio input and output.

keyboard library for capturing keyboard events.

numpy for processing audio data.

You can install the required libraries using the following command:



pip install pyaudio keyboard numpy
Installation
Clone this repository to your local machine:



git clone https://github.com/Saronzeleke/Splitter.git
Navigate to the project directory:


cd Splitter
Install the required dependencies:


pip install -r requirements.txt
# Usage
Run the script by executing:


python split.py
The program will begin recording audio and monitoring your keyboard for keystrokes.

** When the program detects a significant change in the audio amplitude (which could indicate a keystroke), it logs the time and location of the keystroke.

Press the ESC key to stop the recording process. The program will then split the audio file based on the detected keystrokes and save each segment into the split_audio directory.

The program will also log the actual keystrokes detected in the keystroke_log.json file.

# Command-Line Options
The script does not currently accept any command-line arguments. It runs automatically upon execution, starting both the audio recording and keystroke detection.

# Files Generated
Audio segments: Split audio segments are saved in the split_audio folder as .wav files.

Keystroke Log: A JSON file (keystroke_log.json) that records the keystrokes detected during the session, along with timestamps and frame indices.

Example Output

Recording started... Press ESC to stop.
Detected 5 keystrokes by amplitude
Saved segment_1.wav (frames 0-1024)
Saved segment_2.wav (frames 1024-2048)
...
Keystroke log saved to keystroke_log.json
Audio segments saved to 'split_audio' directory
# Notes
The program uses an amplitude threshold (SILENCE_THRESHOLD = 500) to detect keystrokes. This threshold can be adjusted based on the sensitivity required for your environment.

The program listens for keyboard events and logs actual keystrokes during the recording session. This log is saved in keystroke_log.json.

# Troubleshooting
If you encounter an issue where the program doesn't detect keystrokes properly, try adjusting the SILENCE_THRESHOLD value in the script.

Ensure that the necessary libraries (pyaudio, keyboard, numpy) are properly installed.

# License
This project is licensed under the MIT License - see the LICENSE file for details.

Copyright (c) 2025 Saron Zeleke
