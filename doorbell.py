from __future__ import division, print_function
import sys, queue
import numpy as np
import sounddevice as sd
import tensorflow as tf
import params as yamnet_params
import yamnet as yamnet_model
import sounddevice as sd
import time
import logging, os
from datetime import datetime

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
THRESHOLD = 0.5
ANALYSIS_SAMPLE_RATE = 16000
RECORD_SAMPLE_RATE = 48000
ANALYSIS_LENGTH_S = 0.95 # dan ellis approved(tm) analysis window len
BUFFER_SIZE_F = 2048

# Set up homebridge motion plugin to use this
def trigger_homekit_motion():
  os.system("curl 'http://localhost:18089/' >/dev/null 2>&1")

q = queue.Queue()
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(indata[::3, [0]]) # Very bad downsample but it works for this

analysisdata = np.zeros((int(ANALYSIS_LENGTH_S*ANALYSIS_SAMPLE_RATE), 1))
frame_counter = 0

# Copy the latest sound into the analysis window
def update_analysis_window():
    global analysisdata, frame_counter
    while True:
      try:
        data = q.get_nowait()
      except queue.Empty:
        break
      shift = len(data)
      analysisdata = np.roll(analysisdata, -shift, axis=0)
      analysisdata[-shift:, :] = data
      frame_counter += shift


def main(argv):
  global analysisdata, frame_counter
  log = open('/tmp/sound.log','w')
  # Set up yamnet
  params = yamnet_params.Params(sample_rate=ANALYSIS_SAMPLE_RATE, patch_hop_seconds=0.1)
  yamnet = yamnet_model.yamnet_frames_model(params)
  yamnet.load_weights('/home/pi/models/research/audioset/yamnet/yamnet.h5')
  yamnet_classes = yamnet_model.class_names('/home/pi/models/research/audioset/yamnet/yamnet_class_map.csv')
  # Set up a live callback stream from the microphone
  stream = sd.InputStream(device = 1, channels = 1, samplerate=RECORD_SAMPLE_RATE, callback = audio_callback, blocksize = BUFFER_SIZE_F)
  with stream:
    while True:
      update_analysis_window()
      if(frame_counter >= int(ANALYSIS_LENGTH_S * ANALYSIS_SAMPLE_RATE)):
        frame_counter = 0
        scores = yamnet.predict(analysisdata, steps=1)[0]
        if(len(scores)):
          prediction = np.mean(scores, axis=0)
          top5_i = np.argsort(prediction)[::-1][:1]
          for x in top5_i:
            if(prediction[x]>THRESHOLD):
              top_class_str = yamnet_classes[x]
              # Write any detected class (outside these noisy ones) to the log
              if(not top_class_str in ["Fireworks", "Silence", "Inside, small room"]):
                log.write("[%s] %s %0.4f\n" %(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), top_class_str, prediction[x]))
                log.flush()
                # And if it's one of the doorbell ones, ping the homebridge server
                if(top_class_str in ["Beep, bleep", "Doorbell", "Glass", "Sonar", "Ding"]):
                  trigger_homekit_motion()


if __name__ == '__main__':
  main(sys.argv[1:])
