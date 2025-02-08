import streamlit as st
from gtts import gTTS
import base64

# Function to convert text to speech and return the audio file as base64
def text_to_speech(text, lang='en', slow=False):
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save("output.mp3")
    with open("output.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
    return base64.b64encode(audio_bytes).decode("utf-8")

# Streamlit app
def main():
    st.title("Text-to-Speech Converter")
    st.write("Enter text below and click the button to convert it to speech.")

    # Text input
    text = st.text_area("Enter your text here:", "Hello, how are you today?")

    # Language selection
    lang = st.selectbox("Select language:", ["en", "es", "fr", "de", "hi"], index=0)

    # Slow mode toggle
    slow = st.checkbox("Slow mode")

    # Button to convert text to speech
    if st.button("Convert to Speech"):
        if text.strip() == "":
            st.warning("Please enter some text.")
        else:
            st.write("Converting text to speech...")
            audio_base64 = text_to_speech(text, lang=lang, slow=slow)

            # Auto-play the audio using HTML
            audio_html = f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()