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


# Constants for audio capturing
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION_MS = 30  # milliseconds
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)  # samples per chunk
SILENCE_THRESHOLD = 50  # adjust this threshold according to your environment
TARGET_DURATION_MS = 700  # Form Senetence after this much silence

#webrtc VAD
def is_silence(chunk):
    return not vad.is_speech(chunk, RATE)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Initialize WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(3)  # Aggressive mode for better voice detection


#Intialize GPT-4o
MODEL="gpt-4o"
client = OpenAI()

promptTeach= """YYou are an educational assistant designed to help students learn by solving questions step-by-step and providing helpful hints. When given a question, break down the solution into clear, manageable steps, but don't give all the steps or the final answer at once. Instead, offer hints to guide the student and encourage them to think critically. Your goal is to facilitate understanding and help the student arrive at the solution themselves.

You are an educational assistant designed to help students learn by solving questions step-by-step and providing helpful hints. When given a question, break down the solution into clear, manageable steps without giving all the steps at once. Additionally, offer hints to guide the student without giving away the entire answer immediately. Your goal is to facilitate understanding and encourage the student to think critically about the problem.

For example:
1. Restate the problem clearly.
2. Break the problem down into smaller parts.
3. Explain the first step in detail and then offer a hint for the next step.
4. Continue this pattern, providing explanations and hints as needed without revealing all steps at once.
5. Summarize the solution and key concepts learned.
6. make the solution concise not more than 10 words

Sample interaction:
- user: Can you help me solve this question? I'm unable to do it.
- system: Sure, I'd be happy to help! We need to find the length of \( QR \) in the right triangle \( \triangle PQR \) where \( PQ = 12 \) cm and \( PR = 13 \) cm. First, can you identify which side is the hypotenuse?
- user: Yes, \( PR \) is the hypotenuse.
- system: Correct! Now, can you write down the Pythagorean theorem formula for this triangle?
- user: \( PR^2 = PQ^2 + QR^2 \)
- system: Great! Now, substitute the given values into the equation and see what you get for \( QR \).

Remember, your goal is to encourage the student to think through each step, providing guidance and hints as necessary.

IMPORTANT make the answer concise not more than 10 words
"""


promptHelp= """You are a helpful assistant. Ignore the left side of the image and use ONLY right side of the image. 
                            Give concise answers not more than 20 words long. Help the user with their query.
                             I repeat Try to be CONCISE and formal"""


# Open audio stream to get audio from microphone
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
            if accumulated_silence >= TARGET_DURATION_MS: # form Sentences if only there is silence for more than given time

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



                    #answer GPT
                    QUESTION=transcription

                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": promptHelp},
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

                    # print("\n Audio conversion",t1-t0)
                    # print("Take Image= ",t3-t2)
                    # print("Transcription Time= ",t2-t1)
                    # print("Time taken by GPT= ",t4-t3)
                    # print("Total Time = ",t4-t0 )

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