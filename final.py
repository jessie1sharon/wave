from moviepy.editor import *
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
import math
from pydub.utils import make_chunks, mediainfo
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import operator
from functools import reduce
import openai

# Set the path to your JSON key file
key_file_path = r"C:\Users\Jessi\OneDrive\Desktop\ProjectAI\my-project-ai-414117-f611b77bdbbd.json"

# set the api for chatcpt
openai.api_key = 'sk-proj-cuu5xHPn0rcdqtYDOqvDT3BlbkFJXPZtVDjJcf5OtJ9e0ygA'

# Set the environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_file_path

# Load the mp4 file
tk.Tk().withdraw()  # keep the root window from appearing
messagebox.showinfo('Start', 'Please choose an MP4 file')
filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
video = VideoFileClip(filename)

# Extract audio from video
pathname = filename.split('.mp4', 1)[0]
audio_name = pathname + ".mp3"
video.audio.write_audiofile(audio_name)

# convert mp3 file to wav
wav_name = pathname + ".wav"
sound = AudioSegment.from_mp3(audio_name)
sound.export(wav_name, format="wav")


myaudio = AudioSegment.from_file(wav_name, "wav")
# bit1 = mediainfo(wav_name)

duration_in_sec = len(myaudio) / 1000  # Length of audio in sec
bit_rate = 16

wav_file_size = (44100 * bit_rate * 2 * duration_in_sec) / 8

file_split_size = 10000000  # 10Mb OR 10, 000, 000 bytes
total_chunks = wav_file_size // file_split_size  # 27

# Get chunk size by following method
# for  duration_in_sec (X) -->  wav_file_size (Y)
# So whats duration in sec  (K) --> for file size of 10Mb
#  K = X * 10Mb / Y

chunk_length_in_sec = math.ceil((duration_in_sec * 10000000) / wav_file_size)   # in sec
chunk_length_ms = chunk_length_in_sec * 1000
chunks = make_chunks(myaudio, chunk_length_ms)


def transcribe_model_selection(j, n, end1) -> speech.RecognizeResponse:
    once = True

    client = speech.SpeechClient()

    with open(j, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="iw-IL",
        model="Default",
        audio_channel_count=2,
        enable_word_time_offsets=True,
    )

    response = client.recognize(config=config, audio=audio)

    for result1 in response.results:
        transcript1 = result1.alternatives[0]
        transcript = result1.alternatives[0].transcript + "\n"
        for word_info in transcript1.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
        with open("brain_massage.txt", "a+", encoding="utf-8") as txt_file:
            if n == 0:
                txt_file.write(str(start_time) + "\n")
                txt_file.write(transcript)
                end1 = end_time
            else:
                if once:
                    end_iteration = end1  # how to know its the first iteration of n
                    once = False
                times = [start_time, end_iteration]  # the same end1 for all the iteration of n
                start_time = reduce(operator.add, times)
                txt_file.write(str(start_time) + "\n")
                txt_file.write(transcript)
                end_n = [end_time, end_iteration]
                end1 = reduce(operator.add, end_n)  # save the end_time+start time of this n only in the last iteration of n

    return end1


# Export all of the individual chunks as wav files

for i, chunk in enumerate(chunks):
    chunk_name = "chunk{0}.wav".format(i)
    chunk.export(chunk_name, format="wav")


for k in range(0, int(total_chunks)):
    k1 = "chunk{k}.wav".format(k=k)
    if k == 0:
        end2 = transcribe_model_selection(k1, k, 0)
    else:
        end2 = transcribe_model_selection(k1, k, end2)

