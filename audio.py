# cd Documents\01Python\Audiogame

import pyaudio
import wave
import matplotlib.pyplot as plt
import audioop
import numpy as np

import pygame as pg

THRESHOLD = 1000


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100



def listen(bounce_queue):
    print("Keep quiet, shhhhhh")
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    stopped = False
    remaining_frames = -1
    signal = 0
    while True:
        data = stream.read(CHUNK)
        rms = audioop.rms(data, 2)    # here's where you calculate the volume
        if rms > THRESHOLD and not stopped:
            bounce_queue.put(-1)
            stopped = True
            remaining_frames = 50
        
        if remaining_frames > 0:
            signal += rms
            remaining_frames -= 1
        
        elif remaining_frames == 0:
            signal = signal / 100
            bounce_queue.put(signal)
            print(f"Bounce volume {signal}")
            break
        
    stream.stop_stream()
    stream.close()
    p.terminate()