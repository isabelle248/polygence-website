# PART 2 - use pitch tracker to get frequencies from audio input

# Import libraries
import crepe
import librosa
import numpy as np
import matplotlib.pyplot as plt
from music21 import converter
# converter is module in music21 that parses scores from files
import sys

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
time, frequency, confidence, activation = crepe.predict(y, sr, step_size=10, model_capacity='full')


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
print(mxl_file)
score = converter.parse(mxl_file)

# flatten hierarchical structure into a simple sequence (?)
notes = score.flat.notes

# create empty list, each item is a tuple (offset, note_frequency)
note_data = []
all_differences = []
all_times = []

# n is one note (or chord) at a time
for n in notes:
    note_start = (n.offset / tempo) * 60
    note_end = note_start + ((n.quarterLength / tempo) * 60)
    
    # get slice boundaries of CREPE frames that fall in note duration
    # finds first index where time >= note_start
    start_idx = np.searchsorted(filtered_time, note_start, side='left')
    # finds index after last time that is >= note_end
    end_idx = np.searchsorted(filtered_time, note_end, side='right')

    # slice frequency array to get all CREPE pitch values in note duration
    freq_slice = (filtered_freq[start_idx:end_idx]) / 2

    # slice time
    time_slice = filtered_time[start_idx:end_idx]

    # find difference for this slice (sharp = positive, flat = negative)
    difference = freq_slice - n.pitch.frequency

    # add this difference to all_differences array
    all_differences.append(difference)
    all_times.append(time_slice)


# combine all of the difference values
combined_freq = np.concatenate(all_differences)
combined_time = np.concatenate(all_times)

# print results
print(combined_freq)



# #TEST - Plot differences over time
# plt.figure(figsize=(14,6))

# plt.plot(combined_time, combined_freq, label='Frequency difference (Hz)')

# plt.ylabel("Frequency difference (Hz)")

# # turn on grid lines
# plt.grid(True)

# plt.xlabel("Time (s)")
# plt.grid(True)
# plt.tight_layout()
# plt.savefig('uploads/output2_plot.png')
# # # renders + displays plots created
# # plt.show()
