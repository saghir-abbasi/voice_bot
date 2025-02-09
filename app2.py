import streamlit as st
import pyaudio
import wave
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

def record_audio(filename="output.wav", duration=5, rate=44100, chunk=1024, channels=1):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []
    
    st.info("Recording... Speak now")
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    return filename

def recognize_speech(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service."

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

def main():
    st.title("Real-Time Voice-to-Voice AI Assistant")
    
    if st.button("Record & Process Voice"):
        audio_filename = record_audio()
        text = recognize_speech(audio_filename)
        st.write("Recognized Text:", text)
        
        if text:
            audio_file = text_to_speech(text)
            st.audio(audio_file, format='audio/mp3')
            os.remove(audio_file)  # Clean up temp file
        os.remove(audio_filename)  # Clean up recorded file

if __name__ == "__main__":
    main()
