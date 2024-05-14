# Realtime Tutor/Assistant with GPT-4o

This Python script is designed to act as a voice-controlled assistant that uses OpenAI's GPT-4o model It listens for your voice input, transcribes it using OpenAI's Whisper API, captures a screenshot of your current screen, and then helps you with you doubt or questions wheter it is an coding related or Math related or anything that it can capture from your screen.

## Tutorial

**For Teaching Assistant**



https://github.com/Suyash018/Realtime-Tutor-or-Assistant-with-GPT-4o/assets/73903830/a786a83b-e98c-4daa-b7c5-81063ef8826c



**For Normal Assistant**



## Features

- Voice input using PyAudio
- Silence detection using WebRTC VAD
- Audio transcription with OpenAI's Whisper API
- Screenshot capture using PyAutoGUI
- OpenAI's GPT-4o for generating relevant responses based on the transcribed text and captured screen shot

## Requirements

- PyAudio
- WebRTCVAD
- NumPy
- PyDub
- OpenAI
- PyAutoGUI
- Base64

## Usage

1. Install the required Python packages by running `pip install -r requirements.txt`.
2. Obtain an API key from OpenAI and set the `OPENAI_API_KEY` environment variable.
3. Run the script with `python main.py`.
4. Speak your query or question after the "Listening..." prompt appears.
5. The assistant will capture your screen, transcribe your audio, and provide a response based on the transcribed text and the captured image.

## Customization

You can customize the behavior of the assistant by modifying the following constants:

- `FORMAT`, `CHANNELS`, `RATE`: Audio recording settings
- `CHUNK_DURATION_MS`: The duration of each audio chunk in milliseconds
- `SILENCE_THRESHOLD`: The threshold for determining silence in the audio stream
- `TARGET_DURATION_MS`: The duration of silence (in milliseconds) after which the assistant will consider the input complete

Additionally, you can modify the `prompt` variable to change the instructions given to the GPT-4o model.

## Debug
You can easily understand/Debug the code by going through "Broken into modules.ipynb"

## Problems 
- Pyaudio is prone to noise.
- Need to add Silero VAD
- The prompt is very BAD. Please change it to your Liking.
  
## Future Work
- Adding TTS to the model
- Adding Local Whisper to reduce cost.

## Note

This script is for demonstration purposes only and may not be suitable for production environments without further modifications and testing.
