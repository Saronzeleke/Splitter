import numpy as np
import librosa
import soundfile as sf
import os
import json
from datetime import datetime
import argparse

def load_audio(file_path, sample_rate=44100):
    """Load a WAV file and ensure mono and correct sample rate."""
    audio, sr = librosa.load(file_path, sr=sample_rate, mono=True)
    return audio, sr

def detect_keystrokes(audio, sample_rate, amplitude_threshold=0.015, min_gap=0.1, window_size=0.05):
    """Detect keystrokes based on amplitude peaks."""
    # Convert amplitude threshold to normalized scale (librosa audio is [-1, 1])
    threshold = amplitude_threshold * 32768 / np.max(np.abs(audio))  # Relative to audio's max amplitude
    # Compute short-term energy (square of amplitude) for peak detection
    energy = np.abs(audio) ** 2
    # Window size in samples
    window_samples = int(window_size * sample_rate)
    min_gap_samples = int(min_gap * sample_rate)

    # Find peaks in energy
    peaks = []
    last_peak = -min_gap_samples
    for i in range(window_samples, len(audio) - window_samples):
        if (energy[i] > threshold and
            i - last_peak > min_gap_samples and
            energy[i] == max(energy[i - window_samples:i + window_samples])):
            peaks.append(i)
            last_peak = i

    # Convert peaks to time and frame indices
    keystrokes = [
        {
            'sample_index': peak,
            'time': datetime.fromtimestamp(peak / sample_rate).isoformat(),
            'amplitude': float(np.abs(audio[peak]))
        }
        for peak in peaks
    ]
    return peaks, keystrokes

def split_audio(audio, sample_rate, peaks, output_dir, min_segment_duration=0.05):
    """Split audio into segments around detected keystrokes."""
    os.makedirs(output_dir, exist_ok=True)
    segments = []
    min_samples = int(min_segment_duration * sample_rate)

    # Add boundaries (start, peaks, end)
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

    return segments

def save_keystroke_log(keystrokes, log_file):
    """Save detected keystrokes to a JSON file."""
    with open(log_file, 'w') as f:
        json.dump(keystrokes, f, indent=2)

def process_audio_file(input_file, amplitude_threshold=0.015, min_keystroke_gap=0.1, output_dir="split_audio", log_file="keystroke_log.json"):
    """Main function to process a WAV file for keystroke detection and segmentation."""
    print(f"Processing audio file: {input_file}")
    print(f"Amplitude threshold: {amplitude_threshold}, Min keystroke gap: {min_keystroke_gap}s")
    print(f"Output directory: {output_dir}")

    # Load audio
    audio, sample_rate = load_audio(input_file)
    print(f"Loaded audio: {len(audio)} samples, {len(audio)/sample_rate:.2f}s, {sample_rate} Hz")

    # Detect keystrokes
    peaks, keystrokes = detect_keystrokes(audio, sample_rate, amplitude_threshold, min_keystroke_gap)
    print(f"Detected {len(peaks)} keystrokes")

    # Split and save audio segments
    segments = split_audio(audio, sample_rate, peaks, output_dir)
    print(f"Saved {len(segments)} audio segments")

    # Save keystroke log
    save_keystroke_log(keystrokes, log_file)
    print(f"Keystroke log saved to {log_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a WAV file for keystroke detection and segmentation")
    parser.add_argument("--input-file", type=str, required=True, help="Path to the input WAV file")
    parser.add_argument("--amplitude-threshold", type=float, default=0.015, help="Amplitude threshold for keystroke detection (normalized)")
    parser.add_argument("--min-keystroke-gap", type=float, default=0.1, help="Minimum time gap between keystrokes (seconds)")
    parser.add_argument("--output-dir", type=str, default="split_audio", help="Directory to save audio segments")
    parser.add_argument("--log-file", type=str, default="keystroke_log.json", help="File to save keystroke logs")

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
        print(f"Error: {e}")