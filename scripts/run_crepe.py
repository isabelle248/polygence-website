# PART 2 - use pitch tracker to get frequencies from audio input

# Import libraries
import crepe
import librosa
import numpy as np
import matplotlib.pyplot as plt
from music21 import converter
import random
import os
import logging
import json
import math
# converter is module in music21 that parses scores from files
import sys

# Suppress TensorFlow / CREPE / matplotlib warnings and logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Hide TF debug logs
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

mxl_file = sys.argv[1]
audio_path = sys.argv[2]
tempo = int(sys.argv[3])

# Load audio with librosa
# reads audio file from disk, resamples to 16,000 hz
# returns: y - actual audio waveform data (numpy array of floats between -1.0 and 1.0)
# sr - sampling rate (16,000 kHz - 16,000 samples per sec)
y, sr = librosa.load(audio_path, sr=16000)

# Run CREPE pitch tracking on audio waveform (y)
# inputs: y (waveform), sr, step_size=10 (analyze pitch every 10 ms), 
#          model_capacity='full' (highest accuracy CREPE model)
time, frequency, confidence, activation = crepe.predict(y, sr, step_size=7, model_capacity='full')


# adjust time for delay
latency = 0.065
adjusted_time = time - latency
valid_idx = adjusted_time >= 0
adjusted_time = adjusted_time[valid_idx]
adjusted_freq = frequency[valid_idx]
adjusted_conf = confidence[valid_idx]

# filter out values that are less confident
threshold = 0.9
filtered_time = adjusted_time[adjusted_conf > threshold]
filtered_freq = adjusted_freq[adjusted_conf > threshold]


# # PLOTS
# # Plot pitch and confidence
# # Pitch
# # create new blank figure (14 in wide, 6 in tall)
# plt.figure(figsize=(14,6))

# # create grid w/ 2 rows, 1 column, subplot #1 (top)
# plt.subplot(2, 1, 1)

# # draw line graph of detected pitch over time
# # inputs: time (1D numpy array of time points)
# #         frequency (1D array same length of predicted pitches)
# #         label= (adds label for line, use for legend, not y-axis)
# plt.plot(filtered_time, filtered_freq, label='Frequency (Hz)')

# plt.ylabel("Frequency (Hz)")

# # turn on grid lines
# plt.grid(True)

# # Confidence
# plt.subplot(2, 1, 2)
# plt.plot(time, confidence, label='Confidence', color='orange')
# plt.ylabel("Confidence")
# plt.xlabel("Time (s)")
# plt.grid(True)
# plt.tight_layout()
# plt.savefig('/Users/isabellelin/Documents/output_plot.png')
# # renders + displays plots created
# plt.show()


# Compare predicted frequencies to ground truth

# reads MusicXML file and turns it into Score object with notes, rests, measures
# score (object, hierarchical) contains Parts (instruments/voices)
# each Part contains Measures
# each Measure contains Notes or Rests
score = converter.parse(mxl_file)

# flatten hierarchical structure into a simple sequence (?)
notes_and_rests = score.flat.notesAndRests

# create empty list, each item is a tuple (offset, note_frequency)
note_data = []
all_differences = []
all_times = []

measure_numbers = []
note_names = []
cents_list = []
reasoning_lines = []
predicted_freqs = []
note_freqs = []

# Shifts the predicted frequency by octaves until it's closest to the target frequency.
def correct_octave(pred_freq, target_freq):
    # If CREPE outputs 0 (silence), just return 0
    if pred_freq <= 0:
        return pred_freq

    while pred_freq > target_freq * 2:
        pred_freq /= 2
    while pred_freq < target_freq / 2:
        pred_freq *= 2
    return pred_freq

# Shift the times closer to zero until the predicted frequencies match best with ground truth
def shift_times()

def process_note_frequencies(pred_freqs, target_freq):
    # apply correction to each CREPE prediction individually
    corrected = [correct_octave(f, target_freq) for f in pred_freqs if f > 0]

    if not corrected:
        return None
    
    return np.median(corrected)

# n is one note (or chord) at a time
for n in notes_and_rests:

    # store time for rests
    if n.isRest:
        all_times.append((n.offset / tempo) * 60)
        predicted_freqs.append(np.nan)
        note_freqs.append(np.nan)        # keep same length
        continue

    # Skip chords
    if n.isChord:
        continue

    note_start = (n.offset / tempo) * 60
    note_end = note_start + ((n.quarterLength / tempo) * 60)
    
    # get slice boundaries of CREPE frames that fall in note duration
    # finds first index where time >= note_start
    start_idx = np.searchsorted(filtered_time, note_start, side='left')
    # finds index after last time that is >= note_end
    end_idx = np.searchsorted(filtered_time, note_end, side='right')

    # slice frequency array to get all CREPE pitch values in note duration
    freq_slice = (filtered_freq[start_idx:end_idx])

    # slice time
    time_slice = filtered_time[start_idx:end_idx]

    valid_idx = freq_slice > 0
    corrected_freq = np.nan  # default if no valid predictions


    # take median cents difference per note
    if np.any(valid_idx):
        corrected_freq = process_note_frequencies(freq_slice[valid_idx], n.pitch.frequency)
        
        note_cents = 1200 * np.log2(corrected_freq / n.pitch.frequency)
    else:
        # no valid predictions for this note
        note_cents = np.nan 

    # add this difference to all_differences array
    all_differences.append(note_cents)
    all_times.append(note_start)
    predicted_freqs.append(corrected_freq)

    # collect data for feedback output later
    measure_numbers.append(n.measureNumber)
    note_names.append(n.nameWithOctave)
    note_freqs.append(n.pitch.frequency)

    # classify pitch accuracy
    tolerance = 25
    if not np.isnan(note_cents):
        if abs(note_cents) <= tolerance:
            status = "In tune"
        elif note_cents > 0:
            status = "Too sharp"
        else:
            status = "Too flat"
        
        # Store data for reasoning
        reasoning_lines.append(
            f"Measure {n.measureNumber} | {n.nameWithOctave} at {note_start} : {status} ({note_cents:.2f} cents)"
        )

    print(f"Note: {n.nameWithOctave}, Target: {n.pitch.frequency:.2f} Hz, Median Detected: {corrected_freq:.2f} Hz, Cents: {note_cents:.2f}")


def generate_feedback(measures, notes_list, cents_list, times_list, tolerance=25):
    # Dictionary (key is measure number, value is a list of mistakes for that measure)
    mistakes_by_measure = {}

    # Loop through every note
    for measure, note, cents, time in zip(measures, notes_list, cents_list, times_list):
        # Skip missing predictions
        if np.isnan(cents):
            continue

        # Classify in tune, sharp, flat
        if abs(cents) <= tolerance:
            continue
        elif cents > 0:
            tip_options = [
                f"{note} was too sharp ({cents:.1f} cents) at {time:.2f}s - try lowering your finger slightly to bring the pitch down.",
                f"{note} was sharp ({cents:.1f} cents) at {time:.2f}s - practice slowly with a tuner to center the pitch.",
            ]
        else:
            tip_options = [
                f"{note} was too flat ({abs(cents):.1f} cents) at {time:.2f}s - try placing your finger slightly higher to raise the pitch.",
                f"{note} was flat ({abs(cents):.1f} cents) at {time:.2f}s - practice sliding up to the correct pitch using a tuner.",
            ]

        # Randomly choose one of the two tips
        chosen_tip = random.choice(tip_options)

        # Group mistakes by measure
        if measure not in mistakes_by_measure:
            mistakes_by_measure[measure] = []
        mistakes_by_measure[measure].append(chosen_tip)

     # If there are no mistakes, give positive feedback
    if not mistakes_by_measure:
        return "Great job! All of your notes were in tune. Keep up the good work!"
        
    # Build the final feedback string
    feedback = "Feedback:\n\n"
    for measure, mistakes in mistakes_by_measure.items():
        feedback += f"Measure {measure}:\n"
        for mistake in mistakes:
            feedback += f"  - {mistake}\n"
        feedback += "\n"

    return feedback

feedback = generate_feedback(measure_numbers, note_names, all_differences, all_times)
print("\n" + feedback + "\n\n")

# print reasoning
print("Reasoning - Model output for each note:")
print("=" * 40)
print("\n".join(reasoning_lines))
print("=" * 40)

def plot_pitch_comparison(crepe_times, crepe_freqs, note_times, note_freqs, corrected_times, corrected_freqs):
    plt.figure(figsize=(14, 6))

    # Plot CREPE predictions
    plt.scatter(crepe_times, crepe_freqs, color="blue", s=8, alpha=0.6, label="CREPE Predicted Frequency")

    # Plot target (sheet music) frequencies
    plt.scatter(note_times, note_freqs, color="red", s=50, marker="x", label="Target Note Frequencies")

    # Plot corrected crepe predictons
    plt.scatter(corrected_times, corrected_freqs, color="green", s=50, marker="x", label="Corrected CREPE predictions")


    # Make it pretty
    plt.title("Pitch Tracking: CREPE Predictions vs. Target Notes")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.legend()
    plt.grid(True)

    plt.show()

plot_pitch_comparison(filtered_time, filtered_freq, all_times, note_freqs, all_times, predicted_freqs)

for n in notes_and_rests:
    if n.isRest:
        print("rest")
    else:
        print(n.measureNumber, n.nameWithOctave, n.offset, n.quarterLength)



