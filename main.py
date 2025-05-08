import pyaudio
import wave
import numpy as np
import keyboard
from threading import Thread, Event
import time
import os
from collections import deque
import json
from datetime import datetime
import argparse

class AudioSplitter:
    def __init__(self, silence_threshold=500, min_keystroke_gap=0.1, output_dir="split-audio", log_file="keystroke-log.json"):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.SILENCE_THRESHOLD = silence_threshold
        self.MIN_KEYSTROKE_GAP = min_keystroke_gap

        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.stop_event = Event()
        self.keystroke_times = []
        self.actual_keystrokes = []
        self.output_dir = output_dir
        self.log_file = log_file
        
        self.amplitude_window = deque(maxlen=5)
        self.last_keystroke_time = 0

        os.makedirs(self.output_dir, exist_ok=True)

    def callback(self, in_data, frame_count, time_info, status):
        if self.is_recording:
            self.frames.append(in_data)
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            current_amplitude = np.abs(audio_data).mean()
            self.amplitude_window.append(current_amplitude)
            
            if (len(self.amplitude_window) == self.amplitude_window.maxlen and 
                current_amplitude > self.SILENCE_THRESHOLD and
                (time.time() - self.last_keystroke_time) > self.MIN_KEYSTROKE_GAP):
                self.last_keystroke_time = time.time()
                self.keystroke_times.append(len(self.frames) - 1)
        return (in_data, pyaudio.paContinue)

    def start_recording(self):
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.callback
        )
        self.is_recording = True
        print("Recording started... Press ESC to stop.")

    def stop_recording(self):
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        print("Recording stopped.")

    def save_audio_segment(self, filename, start_frame, end_frame):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames[start_frame:end_frame]))
        wf.close()

    def split_by_keystrokes(self):
        if not self.keystroke_times:
            print("No keystrokes detected")
            return
        split_points = [0] + self.keystroke_times + [len(self.frames)]
        for i in range(1, len(split_points)):
            start = split_points[i-1]
            end = split_points[i]
            filename = os.path.join(self.output_dir, f"segment_{i}.wav")
            self.save_audio_segment(filename, start, end)
            print(f"Saved {filename} (frames {start}-{end})")

    def log_actual_keystroke(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            timestamp = datetime.now().isoformat()
            self.actual_keystrokes.append({
                'key': event.name,
                'time': timestamp,
                'frame_index': len(self.frames) if self.is_recording else None
            })
            if len(self.actual_keystrokes) % 5 == 0:
                self.save_keystroke_log()

    def save_keystroke_log(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.actual_keystrokes, f, indent=2)

    def monitor_keys(self):
        keyboard.hook(self.log_actual_keystroke)
        while not self.stop_event.is_set():
            time.sleep(0.1)
        keyboard.unhook_all()

    def run(self):
        print(f"Amplitude threshold: {self.SILENCE_THRESHOLD}")
        print("Press ESC to stop and split by detected keystrokes")
        
        key_thread = Thread(target=self.monitor_keys)
        key_thread.start()
        self.start_recording()
        keyboard.wait('esc')
        self.stop_event.set()
        self.stop_recording()
        key_thread.join()
        print(f"\nDetected {len(self.keystroke_times)} keystrokes by amplitude")
        self.split_by_keystrokes()
        self.save_keystroke_log()
        print(f"\nActual keystrokes logged to {self.log_file}")
        print(f"Audio segments saved to '{self.output_dir}' directory")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio Splitter Configuration")
    parser.add_argument("--silence-threshold", type=int, default=500, help="Amplitude threshold for silence detection")
    parser.add_argument("--keystroke-gap", type=float, default=0.1, help="Minimum time gap between keystrokes in seconds")
    parser.add_argument("--output-dir", type=str, default="split_audio", help="Directory to save audio segments")
    parser.add_argument("--log-file", type=str, default="keystroke_log.json", help="File to save keystroke logs")

    args = parser.parse_args()

    try:
        splitter = AudioSplitter(
            silence_threshold=args.silence_threshold,
            min_keystroke_gap=args.keystroke_gap,
            output_dir=args.output_dir,
            log_file=args.log_file
        )
        splitter.run()
    except Exception as e:
        print(f"Error: {e}")
    