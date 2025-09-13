import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
import pandas as pd
from typing import Optional


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# --- API Configuration ---
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
IMGFLIP_USERNAME = os.getenv('IMGFLIP_USERNAME')
IMGFLIP_PASSWORD = os.getenv('IMGFLIP_PASSWORD')

if not all([GROQ_API_KEY, IMGFLIP_USERNAME, IMGFLIP_PASSWORD]):
    print("Error: Missing required environment variables. Check your .env file.")
    raise ValueError("Missing required environment variables")

# Meme templates
MEME_TEMPLATES = {
    "Drake": "61579",
    "GalaxyBrain": "147635",
    "Pigeon": "100777631",
    "DistractedBoyfriend": "112126428",
    "TwoButtons": "87743020",
    "ExpandingBrain": "93895088",
    "ChangeMyMind": "129242436",
    "UNO": "217743513"
}

# Load syllabus data
try:
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "cbse_stem.csv")
    syllabus_df = pd.read_csv(csv_path, skip_blank_lines=True, quoting=1, quotechar='"', escapechar='\\')
    print("CSV loaded successfully with", len(syllabus_df), "rows!")
except FileNotFoundError:
    
    syllabus_df = pd.DataFrame()
    print("Warning: cbse_stem.csv not found! Using fallback.")
except Exception as e:
    syllabus_df = pd.DataFrame()
    print(f"CSV error: {e}")

# Initialize LangChain LLM for Groq
try:
    llm = ChatOpenAI(
        model="llama-3.1-8b-instant",
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL
    )
    print("LLM initialized successfully with Groq!")
except Exception as e:
    print(f"LLM initialization error: {e}")
    raise

# Prompt template

lesson_prompt = ChatPromptTemplate.from_template("""
Context: {context}
Explain {query} in {subject} in simple {language}, using Gen Alpha slang (e.g., 'lit', 'bussin'), a clean meme reference (e.g., Drake for approve/reject), and an Indian cultural analogy (e.g., Vedic math for math, Diwali rocket for chemistry, monsoon winds for physics).
Keep it fun, educational, max 200 words. End with a 3-question multiple-choice quiz (include answers).
Example: For math, "Quadratics are like choosing the GOAT ladoo at a Diwali party."
""")

lesson_chain = lesson_prompt | llm | StrOutputParser()

def generate_meme(template_name: str, text0: str, text1: str) -> str:
    """Generate a meme using Imgflip API."""
    try:
        template_id = MEME_TEMPLATES.get(template_name, "61579")
        url = "https://api.imgflip.com/caption_image"
        params = {
            "template_id": template_id,
            "username": IMGFLIP_USERNAME,
            "password": IMGFLIP_PASSWORD,
            "text0": text0,
            "text1": text1
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        if response.json().get("success"):
            return response.json()["data"]["url"]
        print(f"Meme API response: {response.json()}")
        return "Meme generation failed."
    except Exception as e:
        print(f"Meme error: {e}")
        return "Meme unavailable, but lesson still slaps!"

def vibe_check_agent(query: str, subject: str, language: str = "English") -> str:
    """Generate lesson and quiz with meme."""
    try:
        # Check if syllabus_df is empty or doesn't have the required columns
        if syllabus_df.empty or "Subject" not in syllabus_df.columns:
            context_str = "No syllabus context available."
        else:
            context = syllabus_df[syllabus_df["Subject"] == subject]["Description"].tolist()
            context_str = f"Context: {', '.join(context[:3])}" if context else "No syllabus context."
        print(f"Context for {subject}: {context_str}")
        lesson = lesson_chain.invoke({"query": query, "subject": subject, "language": language, "context": context_str})
        print(f"Lesson generated: {lesson[:50]}...")  # Debug first 50 chars

        # Generate dynamic meme text based on the lesson content
        meme_prompt = ChatPromptTemplate.from_template("""
        Based on this lesson about {query} in {subject}, create a short, funny meme text for a Drake meme template.
        Return ONLY two short phrases (max 8 words each) separated by a pipe (|):
        First phrase: Something wrong/confusing about the topic
        Second phrase: The right way to understand it

        Example: "Not understanding polynomials" | "Getting the math vibes"
        """)

        meme_chain = meme_prompt | llm | StrOutputParser()
        meme_text = meme_chain.invoke({"query": query, "subject": subject})

        # Parse the meme text
        if "|" in meme_text:
            text0, text1 = meme_text.split("|", 1)
            text0 = text0.strip()
            text1 = text1.strip()
        else:
            # Fallback if parsing fails
            text0 = f"Confused about {query}"
            text1 = f"Understanding {subject} vibes"

        import random
        template_name = random.choice(list(MEME_TEMPLATES.keys()))

        # Template-specific meme prompt instructions
        meme_instructions = {
            "Drake": "Create a short, funny meme text for a Drake meme template. Return ONLY two short phrases (max 8 words each) separated by a pipe (|): First phrase: Something wrong/confusing about the topic. Second phrase: The right way to understand it. Example: 'Not understanding polynomials' | 'Getting the math vibes'",
            "GalaxyBrain": "Create a short, funny meme text for a Galaxy Brain meme template. Return ONLY two short phrases (max 8 words each) separated by a pipe (|): First phrase: A basic/obvious thought about the topic. Second phrase: A next-level or genius insight about the topic. Example: 'Just memorizing formulas' | 'Actually understanding math'",
            "Pigeon": "Create a short, funny meme text for a Pigeon meme template. Return ONLY two short phrases (max 8 words each) separated by a pipe (|): First phrase: A common misconception about the topic. Second phrase: The correct or surprising fact. Example: 'All birds can fly' | 'Penguins are birds too'",
            "DistractedBoyfriend": "Create a short, funny meme text for a Distracted Boyfriend meme template. Return ONLY two short phrases (max 8 words each) separated by a pipe (|): First phrase: The thing you should focus on. Second phrase: The thing that distracts you. Example: 'Studying for finals' | 'Scrolling memes'",
            "TwoButtons": "Create a short, funny meme text for a Two Buttons meme template. Return ONLY two short phrases (max 8 words each) separated by a pipe (|): First phrase: The first difficult choice. Second phrase: The second difficult choice. Example: 'Do homework' | 'Take a nap'",
            "ExpandingBrain": "Create a short, funny meme text for an Expanding Brain meme template. Return ONLY two short phrases (max 8 words each) separated by a pipe (|): First phrase: A basic/normal way to do something. Second phrase: A galaxy-brain/next-level way. Example: 'Using calculator' | 'Mental math like a boss'",
            "ChangeMyMind": "Create a short, funny meme text for a Change My Mind meme template. Return ONLY two short phrases (max 8 words each) separated by a pipe (|): First phrase: A controversial or funny opinion. Second phrase: A challenge or rebuttal. Example: 'Math is fun' | 'Change my mind'",
            "UNO": "Create a short, funny meme text for a UNO Draw 25 meme template. Return ONLY two short phrases (max 8 words each) separated by a pipe (|): First phrase: Something you refuse to do. Second phrase: The consequence (Draw 25). Example: 'Do my homework' | 'Draw 25'"
        }
        meme_prompt_text = f"""
        Based on this lesson about {{query}} in {{subject}}, {meme_instructions[template_name]}
        """
        meme_prompt = ChatPromptTemplate.from_template(meme_prompt_text)
        meme_chain = meme_prompt | llm | StrOutputParser()
        meme_text = meme_chain.invoke({"query": query, "subject": subject})

        # Parse the meme text
        if "|" in meme_text:
            text0, text1 = meme_text.split("|", 1)
            text0 = text0.strip()
            text1 = text1.strip()
        else:
            # Fallback if parsing fails
            text0 = f"Confused about {query}"
            text1 = f"Understanding {subject} vibes"

        meme_url = generate_meme(template_name, text0, text1)
        print(f"Meme template used: {template_name}")
        print(f"Meme URL: {meme_url}")
        return f"{lesson}\n\n**Meme Quiz Vibes**: Check this out: {meme_url}"
    except Exception as e:
        print(f"Agent error: {e}")
        return f"Oops, something’s not vibin’! Try again with query: {query}"

def transcribe_voice(audio_file: str, language: str = "en") -> Optional[str]:
    """Transcribe voice input (Not supported by Groq)."""
    print("Voice transcription is not supported by Groq API.")
    return None

def analyze_image(image_data: bytes, query: str, subject: str) -> Optional[str]:
    """Analyze diagram (Not supported by Groq)."""
    print("Image analysis is not supported by Groq API.")
    return "Diagram analysis not supported by Groq API."

if __name__ == "__main__":
    print("Testing VibeCheck Agent...")
    result = vibe_check_agent("What are polynomials?", "Math", "English")
    print(result)
