import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import base64
import time
from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import google.generativeai as genai
import re

# Configuration
GEMINI_API_KEY = "AIzaSyBJ7p50gVeFIRVecnuDyOq---2RwVfGgdM"
MODEL_NAME = "gemini-2.0-flash-exp"
genai.configure(api_key=GEMINI_API_KEY)

@dataclass
class AppState:
    chat_history: list
    recipe_steps: list
    current_step: int
    is_listening: bool
    awaiting_confirmation: bool

def initialize_state():
    return AppState(
        chat_history=[],
        recipe_steps=[],
        current_step=0,
        is_listening=False,
        awaiting_confirmation=False
    )

if "app_state" not in st.session_state:
    st.session_state.app_state = initialize_state()

@st.cache_resource
def load_model():
    return ChatGoogleGenerativeAI(model=MODEL_NAME, api_key=GEMINI_API_KEY)

llm = load_model()

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are a professional chef assistant. Follow these rules:\n"
               "1. Provide numbered step-by-step cooking instructions\n"
               "2. Each step must start with 'Step X:' on a new line\n"
               "3. After each step, add: '[NEXT]' on a separate line\n"
               "4. Keep steps concise (1-2 sentences each)\n"
               "5. If asked about non-cooking topics, respond: 'I specialize in cooking advice only!'"),
    ("human", "{input}")
])

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            st.toast("Listening...", icon="🎤")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            st.error("Could not understand audio. Please try again.")
            return None
        except (sr.RequestError, sr.WaitTimeoutError) as e:
            st.error(f"Error: {str(e)}")
            return None

def parse_steps(response_text):
    steps = []
    pattern = r"Step \d+:(.*?)(?=\nStep \d+:|\[NEXT\]|\Z)"
    matches = re.findall(pattern, response_text, flags=re.DOTALL)
    for match in matches:
        step = match.strip()
        if step:
            steps.append(step)
    return steps if steps else [response_text]

def generate_ai_response(user_input):
    try:
        chain = PROMPT_TEMPLATE | llm
        response = chain.invoke({"input": user_input})
        return parse_steps(response.content)
    except Exception as e:
        st.error(f"AI response error: {str(e)}")
        return ["Sorry, I encountered an error. Please try again."]

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save("output.mp3")
        with open("output.mp3", "rb") as audio_file:
            return base64.b64encode(audio_file.read()).decode("utf-8")
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None

def play_audio(text):
    audio_base64 = text_to_speech(text)
    if audio_base64:
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.components.v1.html(audio_html, height=0)
        time.sleep(3)  # Allow time for audio to play

def main():
    st.title("👩🍳 AI Cooking Assistant")
    st.write("Say 'NEXT' to continue through recipe steps!")
    
    with st.container(height=400, border=True):
        for speaker, text in st.session_state.app_state.chat_history:
            st.chat_message(speaker).write(text)
    
    # Main interaction state machine
    if st.session_state.app_state.is_listening:
        user_input = recognize_speech()
        st.session_state.app_state.is_listening = False
        
        if user_input:
            st.session_state.app_state.chat_history.append(("You", user_input))
            
            if user_input in ["next", "continue"] and st.session_state.app_state.awaiting_confirmation:
                st.session_state.app_state.current_step += 1
                st.session_state.app_state.awaiting_confirmation = False
            elif not st.session_state.app_state.recipe_steps:
                with st.spinner("🧑🍳 Preparing your recipe..."):
                    st.session_state.app_state.recipe_steps = generate_ai_response(user_input)
                st.session_state.app_state.current_step = 0

        # Process current step
        if st.session_state.app_state.current_step < len(st.session_state.app_state.recipe_steps):
            current_step = st.session_state.app_state.recipe_steps[st.session_state.app_state.current_step]
            st.session_state.app_state.chat_history.append(("Assistant", current_step))
            play_audio(current_step + ". Say NEXT to continue")
            st.session_state.app_state.awaiting_confirmation = True
            st.session_state.app_state.is_listening = True
        else:
            play_audio("Recipe completed! What would you like to cook next?")
            st.session_state.app_state = initialize_state()
        
        st.rerun()
    
    if not st.session_state.app_state.recipe_steps and st.button("🎤 Start Cooking Session"):
        st.session_state.app_state.is_listening = True
        st.rerun()

if __name__ == "__main__":
    main()