import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import io
import wave
import re

# ====================== CONFIG ======================
st.set_page_config(page_title="✨ StoryMate : Magical Stories ✨", page_icon="🧚", layout="wide")
load_dotenv()
client = genai.Client()

# Custom magical CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        font-size: 3.5rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #FFD93D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Georgia', serif;
        margin-bottom: 10px;
    }
    .story-card {
        background: linear-gradient(145deg, #1E1E2E, #2A2A40);
        border: 4px solid #FF69B4;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 15px 35px rgba(255, 105, 180, 0.4);
        margin-bottom: 20px;
        color: white;
    }
    .scene-title {
        color: #00FFAA;
        text-align: center;
        font-size: 1.8rem;
        text-shadow: 0 0 10px #00FFAA;
    }
</style>
""", unsafe_allow_html=True)

# ====================== HELPERS ======================
def generate_story(topic: str) -> str:
    prompt = f"""Create an enchanting short story about "{topic}".
Divide it EXACTLY into THREE scenes.
Output format MUST be exactly:

**Scene 1:** 
[vivid 120-word text]

**Scene 2:** 
[vivid 120-word text]

**Scene 3:** 
[vivid 120-word text]

Make it magical, emotional, and perfect for narration."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

def parse_scenes(full_story: str):
    pattern = r'\*\*Scene \d+:\*\*\s*(.*?)(?=\*\*Scene \d+:|\Z)'
    matches = re.findall(pattern, full_story, re.DOTALL | re.IGNORECASE)
    return [m.strip() for m in matches if m.strip()][:3]

def generate_image(scene_text: str, scene_num: int) -> bytes:
    img_prompt = f"A breathtaking storybook-style illustration for Scene {scene_num}: {scene_text[:280]}. Vibrant colors, fantasy style, highly detailed, magical atmosphere, perfect for children."
    response = client.models.generate_images(
        model="imagen-4.0-ultra-generate-001",
        prompt=img_prompt,
        config=types.GenerateImagesConfig(number_of_images=1)
    )
    return response.generated_images[0].image.image_bytes

def generate_narration(story_text: str) -> bytes:
    prompt = f"Narrate this complete story in a warm, enchanting, storytelling voice with emotion and clear pronunciation: {story_text}"
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                )
            )
        )
    )
    pcm_data = response.candidates[0].content.parts[0].inline_data.data
    
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    buffer.seek(0)
    return buffer.read()

# ====================== UI ======================
st.markdown('<h1 class="main-header">✨ StoryMate: Magical Story Weaver ✨</h1>', unsafe_allow_html=True)
st.markdown("### Turn any idea into a 3-scene illustrated fairy tale with voice narration")

topic = st.text_input("🌟 Enter your story topic", 
                      placeholder="A brave fox who discovers a hidden star portal...",
                      label_visibility="collapsed")

if st.button("🪄 Generate Magical Story", type="primary", use_container_width=True):
    if not topic.strip():
        st.error("Please enter a topic!")
    else:
        with st.spinner("Weaving the magic..."):
            full_story = generate_story(topic)
            scenes = parse_scenes(full_story)
            
            if len(scenes) < 3:
                st.error("Story generation issue — Gemini didn't follow the 3-scene format. Try again!")
                st.stop()
            
            st.session_state.full_story = full_story
            st.session_state.scenes = scenes
            
        with st.spinner("Painting 3 breathtaking illustrations..."):
            images = []
            for i, scene in enumerate(scenes, 1):
                img_bytes = generate_image(scene, i)
                images.append(img_bytes)
            st.session_state.images = images
        
        st.success("✨ Your magical story is ready!")
        st.balloons()

# ====================== DISPLAY ======================
if "scenes" in st.session_state:
    # AUDIO SECTION — at the top
    st.markdown("### 🔊 Full Story Narration")
    if st.button("🧚‍♀️ Let the Enchanted Narrator Speak", type="secondary", use_container_width=True):
        with st.spinner("The storyteller is bringing your tale to life..."):
            audio_bytes = generate_narration(st.session_state.full_story)
            st.session_state.audio_bytes = audio_bytes
        st.success("Narration complete!")
    
    if "audio_bytes" in st.session_state:
        st.audio(st.session_state.audio_bytes, format="audio/wav")
        st.download_button(
            label="📥 Download Narration (.wav)",
            data=st.session_state.audio_bytes,
            file_name="enchanted_story_narration.wav",
            mime="audio/wav",
            use_container_width=True
        )

    st.divider()
    st.markdown("### 📖 Your 3-Scene Magical Tale")

    cols = st.columns(3)
    for i, (scene_text, img_bytes) in enumerate(zip(st.session_state.scenes, st.session_state.images)):
        with cols[i]:
            st.markdown(f"""
            <div class="story-card">
                <h3 class="scene-title">Scene {i+1} ✨</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(scene_text)
            
            st.image(
                img_bytes,
                caption=f"Scene {i+1} Illustration",
                use_container_width=True
            )

    st.caption("Powered by Gemini 2.0 Flash • Imagen 4 Ultra • Gemini 2.5 Flash Preview TTS • Crafted with magic for story lovers")
