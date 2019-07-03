#!/usr/bin/python
# -*- coding: UTF-8 -*-

import librosa
import librosa.display
import numpy as np
from pygame import mixer 
import threading
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.animation as animation

def playmp3():
	mixer.init()
	mixer.music.load('./demo.mp3')
	mixer.music.play()

playThread = threading.Thread(target=playmp3)

y, sr = librosa.load("./demo.mp3", sr=None)
duration = librosa.get_duration(y=y, sr=sr)
# 音频时长，单位秒
print duration
# 音频采样率
print sr
S = np.abs(librosa.stft(y))
# 频率、振幅强度，横坐标是采样点，纵坐标是帧
pitches, magnitudes = librosa.piptrack(S=S, sr=sr)
# 八音12度的强度
chroma_st = librosa.feature.chroma_stft(S=S, sr=sr)

def detect_pitch(t):
  index = magnitudes[:, t].argmax()
  pitch = pitches[index, t]
  return pitch

chromas = []
for x in range(len(chroma_st[0])):
	sts = []
	for st in chroma_st:
		sts.append(int(st[x]))
	chromas.append(sts)


# 起点强度（音符按键起始点）
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
# 节拍点（帧索引）
tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
# 节拍点 （时间点，单位秒）
beat_times = librosa.frames_to_time(beats, sr=sr)
# 节拍点的音高
beat_pitches = []
# 节拍点的八音12度的强度
beat_chroma_st = []
for beat in beats:
	beat_pitches.append(detect_pitch(beat))

	chromas = []
	for chr_st in chroma_st:
		chromas.append(chr_st[beat])
	beat_chroma_st.append(chromas)

# playThread.start()
# pre_beat_time = 0
# index = 0
# for beat_time in beat_times:
# 	sleep(beat_time - pre_beat_time)

# 	# print beat_pitches[index]
	
# 	sts = "";
# 	for st in beat_chroma_st[index]:
# 		sts += '%d ,' %st 
# 	print sts

# 	pre_beat_time = beat_time
# 	index += 1


# 直方图
def create_path_data(data):
	temp_path_data = []
	for x in range(len(data)):
		temp_path_data.append((path.Path.MOVETO,(0.75 + x, 0)))
		temp_path_data.append((path.Path.LINETO,(0.75 + x, data[x])))
		temp_path_data.append((path.Path.LINETO,(1.25 + x, data[x])))
		temp_path_data.append((path.Path.LINETO,(1.25 + x, 0)))
	temp_path_data.append((path.Path.CLOSEPOLY,(1.25 + len(data), 0)))
	return temp_path_data

fig, ax = plt.subplots()
data = np.zeros(12)
path_data = create_path_data(data)
codes, temp_verts = zip(*path_data)

verts = np.zeros((12 * 4 + 1, 2))

for x in range(len(temp_verts)):
	verts[x] = list(temp_verts[x])

patch = None
pre_beat_time = 0
def animate(i):
	global pre_beat_time
	if i == 0 and pre_beat_time != 0:
		playThread.start()

	data = beat_chroma_st[i]
	for x in range(len(data)):
		verts[x * 4 + 1][1] = data[x]
		verts[x * 4 + 2][1] = data[x]

	beat_time = beat_times[i]
	sleep_time = beat_time - pre_beat_time
	if sleep_time > 0.12:
		sleep_time -= 0.12
	sleep(sleep_time)
	pre_beat_time = beat_time

	return [patch, ]

barpath = path.Path(verts, codes)
patch = patches.PathPatch(barpath, facecolor='green', edgecolor='yellow', alpha=0.8)
ax.add_patch(patch)

ax.set_xlim(0, 13)
ax.set_xticks(range(0, 13))
ax.set_ylim(0, 1)

ani = animation.FuncAnimation(fig, animate, len(beats), repeat=False, blit=True)
plt.grid(True)

plt.show()


# 音频起始点
# onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
# onset_times = librosa.frames_to_time(onset_frames, sr=sr)
# onset_env = librosa.onset.onset_strength(y=y, sr=sr, feature=librosa.cqt)

# onset_pitches = []
# onset_chroma_st = []
# for onset_frame in onset_frames:
# 	onset_pitches.append(detect_pitch(onset_frame));
# 	chromas = []
# 	for chr_st in chroma_st:
# 		chromas.append(chr_st[onset_frame])
# 	onset_chroma_st.append(chromas)

# onset_notes = librosa.hz_to_note(onset_pitches)

# playThread.start()
# pre_onset_time = 0
# index = 0
# for onset_time in onset_times:
# 	sleep(onset_time - pre_onset_time)
# 	# print onset_pitches[index]

# 	sts = "";
# 	for st in onset_chroma_st[index]:
# 		sts += '%d ,' %st 
# 	print sts
# 	pre_onset_time = onset_time
# 	index += 1



 
# y_harm, y_perc = librosa.effects.hpss(y)
# plt.figure()
# librosa.display.waveplot(y_harm, sr=sr, alpha=0.25)
# librosa.display.waveplot(y_perc, sr=sr, color='b', alpha=0.5)
# plt.title('Harmonic + Percussive')
# plt.show()




# melspec = librosa.feature.melspectrogram(y=y, sr=sr, hop_length=512, n_mels = 64)
# logmelspec = librosa.power_to_db(melspec)
# plt.figure()
# librosa.display.specshow(logmelspec, sr=sr, x_axis='time', y_axis='mel')
# librosa.display.waveplot(y, sr)
# plt.title('Beat wavform')
# plt.show()



# plt.figure()
# C = np.abs(librosa.cqt(y, sr=sr))
# D = librosa.amplitude_to_db(C, ref=np.max)
# librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='cqt_note')
# plt.colorbar(format='%+2.0f dB')
# plt.title('Constant-Q power spectrum')
# plt.show()