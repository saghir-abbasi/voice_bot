import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
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
    st.title("Voice-to-Voice AI Assistant")
    
    if st.button("Speak Now"):
        text = recognize_speech()
        st.write("Recognized Text:", text)
        
        if text:
            audio_file = text_to_speech(text)
            st.audio(audio_file, format='audio/mp3')
            os.remove(audio_file)  # Clean up temp file

if __name__ == "__main__":
    main()
