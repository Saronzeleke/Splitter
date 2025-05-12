import numpy as np
import librosa
import soundfile as sf
import os
import json
from datetime import datetime
import argparse
import traceback


def load_audio(file_path, sample_rate=44100):
    print(f"Loading audio from {file_path}")
    try:
        audio, sr = librosa.load(file_path, sr=sample_rate, mono=True)
        print(f"Audio loaded: {len(audio)} samples, {len(audio)/sr:.2f}s, {sr} Hz")
        print(f"Max amplitude: {np.max(np.abs(audio)):.6f}, Mean energy: {np.mean(np.abs(audio) ** 2):.6f}")
        return audio, sr
    except Exception as e:
        print(f"Error loading audio: {e}")
        raise

def detect_keystrokes(audio, sample_rate, amplitude_threshold=0.005, min_gap=0.05, window_size=0.02):
    print("Detecting peaks...")
    try:
        energy = np.abs(audio) ** 2
        window_samples = int(window_size * sample_rate)
        min_gap_samples = int(min_gap * sample_rate)
        print(f"Window size: {window_samples} samples ({window_size}s)")
        print(f"Min gap: {min_gap_samples} samples ({min_gap}s)")
        print(f"Max energy: {np.max(energy):.6f}, Mean energy: {np.mean(energy):.6f}")

      
        peaks = []
        last_peak = -min_gap_samples

        for i in range(window_samples, len(audio) - window_samples):
            if (energy[i] > amplitude_threshold and
                i - last_peak > min_gap_samples and
                energy[i] == max(energy[i - window_samples:i + window_samples])):
                peaks.append(i)
                last_peak = i
                print(f"Peak at sample {i} ({i/sample_rate:.2f}s), energy: {energy[i]:.6f}")

        keystrokes = [
            {
                'sample_index': peak,
                'time': str(round(peak / sample_rate, 3)) + "s",
                'amplitude': float(np.abs(audio[peak]))
            }
            for peak in peaks
        ]
        print(f"Detection complete: {len(peaks)} peaks found")
        return peaks, keystrokes
    except Exception as e:
        print(f"Error in detect_keystrokes: {e}")
        raise

def split_audio(audio, sample_rate, peaks, output_dir, min_segment_duration=0.05):
    print(f"Splitting audio, saving to {output_dir}")
    try:
        os.makedirs(output_dir, exist_ok=True)
        segments = []
        min_samples = int(min_segment_duration * sample_rate)

        split_points = [0] + peaks + [len(audio)]
        for i in range(1, len(split_points)):
            start = max(0, split_points[i - 1] - min_samples // 2)
            end = min(len(audio), split_points[i] + min_samples // 2)
            if end - start >= min_samples:
                segment = audio[start:end]
                filename = os.path.join(output_dir, f"segment_{i}.wav")
                sf.write(filename, segment, sample_rate)
                segments.append((filename, start, end))
                print(f"Saved {filename} (samples {start}-{end}, duration {(end-start)/sample_rate:.2f}s)")

        print(f"Audio splitting complete: {len(segments)} segments saved")
        return segments
    except Exception as e:
        print(f"Error in split_audio: {e}")
        raise

def save_keystroke_log(keystrokes, log_file):
    print(f"Saving keystroke log to {log_file}")
    try:
        with open(log_file, 'w') as f:
            json.dump(keystrokes, f, indent=2)
        print("Keystroke log saved")
    except Exception as e:
        print(f"Error saving keystroke log: {e}")
        raise

def process_audio_file(input_file, amplitude_threshold=0.005, min_keystroke_gap=0.05, output_dir="split_audio_test", log_file="keystroke_log_1.json"):
    print(f"Processing audio file: {input_file}")
    print(f"Amplitude threshold: {amplitude_threshold}, Min keystroke gap: {min_keystroke_gap}s")
    print(f"Output directory: {output_dir}")

    audio, sample_rate = load_audio(input_file)
    peaks, keystrokes = detect_keystrokes(audio, sample_rate, amplitude_threshold, min_keystroke_gap)
    segments = split_audio(audio, sample_rate, peaks, output_dir)
    save_keystroke_log(keystrokes, log_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test a WAV file for keystroke detection and segmentation")
    parser.add_argument("--input-file", type=str, required=True, help="Path to the input WAV file")
    parser.add_argument("--amplitude-threshold", type=float, default=0.005, help="Amplitude threshold for detection (normalized)")
    parser.add_argument("--min-keystroke-gap", type=float, default=0.05, help="Minimum time gap between detections (seconds)")
    parser.add_argument("--output-dir", type=str, default="split_audio_test", help="Directory to save audio segments")
    parser.add_argument("--log-file", type=str, default="keystroke_log_1.json", help="File to save keystroke logs")

    args = parser.parse_args()

    try:
        process_audio_file(
            input_file=args.input_file,
            amplitude_threshold=args.amplitude_threshold,
            min_keystroke_gap=args.min_keystroke_gap,
            output_dir=args.output_dir,
            log_file=args.log_file
        )
    except Exception as e:
        print(f"Error in process_audio_file: {e}")
        traceback.print_exc()
