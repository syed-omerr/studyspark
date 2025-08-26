import openai
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
from typing import Optional

# Initialize OpenAI client (replace with your API key or use environment variable)
openai.api_key = "your-openai-key"  # Set via environment variable or workshop key

# Imgflip API credentials (replace with your own, get from imgflip.com/api)
IMGFLIP_USERNAME = "your-imgflip-username"
IMGFLIP_PASSWORD = "your-imgflip-password"

# Meme templates (clean, judge-friendly)
MEME_TEMPLATES = {
    "Drake": "61579",           # Drake Hotline Bling
    "GalaxyBrain": "147635",    # Expanding Brain
    "Pigeon": "100777631"       # Is This a Pigeon?
}

# Initialize LangChain LLM with GPT-4o-mini
llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai.api_key)

# Prompt template for generating lessons with Gen Z flair
lesson_prompt = ChatPromptTemplate.from_template("""
Explain {query} for CBSE grade 8 {subject} in simple {language}, using Gen Z slang (e.g., 'lit', 'bussin'), a clean meme reference (e.g., Drake for approve/reject), and an Indian cultural analogy (e.g., Vedic math for math, Diwali rocket for chemistry, monsoon winds for physics).
Keep it fun, educational, max 200 words. End with a 3-question multiple-choice quiz (include answers).
Example: For math, "Quadratics are like choosing the GOAT ladoo at a Diwali party."
""")

# Chain for lesson generation
lesson_chain = lesson_prompt | llm | StrOutputParser()

def generate_meme(template_name: str, text0: str, text1: str) -> str:
    """Generate a meme using Imgflip API."""
    try:
        template_id = MEME_TEMPLATES.get(template_name, "61579")  # Default to Drake
        url = "https://api.imgflip.com/caption_image"
        params = {
            "template_id": template_id,
            "username": IMGFLIP_USERNAME,
            "password": IMGFLIP_PASSWORD,
            "text0": text0,
            "text1": text1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        if response.json().get("success"):
            return response.json()["data"]["url"]
        return "Meme generation failed."
    except Exception as e:
        print(f"Meme error: {e}")
        return "Meme unavailable, but lesson still slaps!"

def vibe_check_agent(query: str, subject: str, language: str = "English") -> str:
    """Main agent to generate lesson and quiz with meme integration."""
    try:
        # Run lesson chain
        lesson = lesson_chain.invoke({"query": query, "subject": subject, "language": language})
        
        # Choose meme based on subject
        meme_map = {
            "Math": ("Drake", "Wrong equation", "Right equation with Vedic math"),
            "Physics": ("GalaxyBrain", "Basic motion", "Newton’s laws with monsoon vibes"),
            "Chemistry": ("Pigeon", "Wrong reaction", "Balanced equation like Diwali rockets")
        }
        template, text0, text1 = meme_map.get(subject, ("Drake", "Wrong answer", "Right answer"))
        meme_url = generate_meme(template, text0, text1)
        
        return f"{lesson}\n\n**Meme Quiz Vibes**: Check this out: {meme_url}"
    except Exception as e:
        print(f"Agent error: {e}")
        return f"Oops, something’s not vibin’! Try again with query: {query}"

def transcribe_voice(audio_file: str) -> Optional[str]:
    """Transcribe voice input using Whisper API."""
    try:
        with open(audio_file, "rb") as f:
            transcript = openai.audio.transcriptions.create(model="whisper-1", file=f)
        return transcript.text
    except Exception as e:
        print(f"Whisper error: {e}")
        return None

def analyze_image(image_data: bytes, query: str, subject: str) -> Optional[str]:
    """Analyze student-drawn diagram using Vision API."""
    try:
        # For local testing, assume image_data is bytes; for deployment, convert to base64 if needed
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analyze this {query} diagram for CBSE grade 8 {subject}. Provide feedback (max 100 words)."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data.decode()}"}}  # Adjust for actual base64
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Vision error: {e}")
        return "Diagram analysis failed, but keep sketchin’, fam!"