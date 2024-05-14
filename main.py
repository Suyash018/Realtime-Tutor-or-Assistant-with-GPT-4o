# Initialization pyaudio for microphone and Webrtc vad

# pyaudio audio
import pyaudio
import webrtcvad
import numpy as np
from pydub import AudioSegment
from io import BytesIO

# Image
import base64
import pyautogui

#GPT and Transcribe
from openai import OpenAI 

import time


# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION_MS = 30  # milliseconds
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)  # samples per chunk
SILENCE_THRESHOLD = 50  # adjust this threshold according to your environment
TARGET_DURATION_MS = 700  # milliseconds

def is_silence(chunk):
    return not vad.is_speech(chunk, RATE)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Initialize WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(3)  # Aggressive mode for better voice detection







from io import BytesIO
import base64
import pyautogui
from openai import OpenAI 


MODEL="gpt-4o"
client = OpenAI()



# Open stream
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                     input=True, frames_per_buffer=CHUNK_SIZE)

print("Listening...")

try:
    accumulated_data = b""
    accumulated_silence = 0
    while True:
        chunk = stream.read(CHUNK_SIZE) #read mic data
        is_silent = is_silence(chunk)
        if is_silent:
            accumulated_silence += CHUNK_DURATION_MS
            if accumulated_silence >= TARGET_DURATION_MS:

                if accumulated_data != b"" :
                    t0 = time.time()
                    
                    #audio
                    audio_stream = BytesIO(accumulated_data)
                    audio_segment = AudioSegment.from_file(audio_stream, format='raw',
                                        frame_rate=16000, channels=1, sample_width=2)
                    audio_segment.export('output.wav', format='wav')
                    audio_file = open("output.wav", "rb")
                    t1 = time.time()

                    #openai Transcribe
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file, 
                        response_format="text"
                        )
                    print("Question = ",transcription)
                    t2 = time.time()




                    # Take Screen Shots
                    photo = pyautogui.screenshot()
                    output = BytesIO()
                    photo.save(output, format='PNG')
                    im_data = output.getvalue()
                    image_data = base64.b64encode(im_data).decode("utf-8")

                    t3= time.time()




                    QUESTION=transcription

                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": """You are a helpful assistant. Ignore the left side of the image and use ONLY right side of the image. 
                             HELP the student to THINK. SEE if he is solving the question correctly.
                             DONOT solve the whole Question give him steps and HINT to solve it.
                             Give concise answers not more than 20 words long. Use the image as a reference to check if they are going the right way.
                             I repeat Try to be CONCISE"""},
                            {"role": "user", "content": [
                                {"type": "text", "text": QUESTION},
                                {"type": "image_url", "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"}
                                }
                            ]}
                        ],
                        temperature=0.0,
                    )

                    t4= time.time()

                    


                    print("GPT answer= ",response.choices[0].message.content)
                # segments, info = model.transcribe('output.wav', beam_size=5)
                # print(segments)
                    print("\n Audio conversion",t1-t0)
                    print("Take Image= ",t3-t2)
                    print("Transcription Time= ",t2-t1)
                    print("Time taken by GPT= ",t4-t3)
                    print("Total Time = ",t4-t0 )

                    accumulated_data=b""


                #print("No sound detected for {} milliseconds".format(accumulated_silence))
                accumulated_silence = 0  # Reset accumulated silence after printing message
        else:
            accumulated_data += chunk
            accumulated_silence = 0  # Reset accumulated silence if sound is detected
except KeyboardInterrupt:
    pass

# Cleanup
print("Stopping...")
stream.stop_stream()
stream.close()
audio.terminate()