import json
import random
import os
import typing import List, dict, Any, Optional
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel

#Configuration
PROCESSED_DATA_FILE = "processed_bible_data.json"
AGENT_BASE_URL = "YOUR_PUBLIC_URL_HERE"

# Initialize the OpenAI client (it will automatically use the OPENAI_API_KEY environment variable)
CLIENT = OpenAI() 
MODEL = "gpt-4.1-mini"

# --- Data Loading and Preprocessing ---
class BibleVerse:
    def __init__(self, reference: str, text: str):
        self.reference = reference
        self.text = text

def load_bible_data() -> List[BibleVerse]:
    """Loads the processed Bible data into a list of BibleVerse objects."""
    try:
        with open(PROCESSED_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [BibleVerse(v['reference'], v['text']) for v in data]
    except FileNotFoundError:
        print(f"Error: Processed data file not found at {PROCESSED_DATA_FILE}")
        return []

Bible_Verses = load_bible_data()

#---Core Agent Logic ---
def get_verse_by_mood(mood_description: str) -> Optional[BibleVerse]:
    """
    Uses an LLM to select a relevant Bible verse based on the user's mood.
    """
    if not BIBLE_VERSES:
        return None
    
    # 1. LLM to generate a search query/theme
    system_prompt = (
        "You are a spiritual guide. A user will describe their mood. "
        "Your task is to respond with a single, short, comma-separated list of 3-5 keywords "
        "that represent the spiritual theme or topic that would be most comforting, encouraging, "
        "or relevant to the user's described mood. "
        "Example: 'I feel sad but hopeful' -> 'hope, perseverance, comfort, strength, future'"
    )
    try:
        response = CLIENT.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mood_description}
            ],
            temperature=0.7,
            max_tokens=50
        )

        keywords_str = response.choices[0].message.content.strip().lower()
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
    except Exception as e:
        print(f"LLM call failed: {e}")
        keywords = []
    
    #. Perform  Keyword search
    if keywords:
        matching_verses = []
        for verse in BIBLE_VERSES:
            # Simple matching: check if any keyword is in the verse text
            if any(keyword in verse.text.lower() for keyword in keywords):
                matching_verses.append(verse)
        
        if matching_verses:
            # Return a random verse from the matching set
            return random.choice(matching_verses)

    #3. Just return a random text
    print("Falling back to random verse.")
    return random.choice(BIBLE_VERSES)

# --- Telex.im A2A Protocol Implementation (FastAPI) ---
app = FastAPI(
    title="Daily Bible Verse Agent", 
    description="An AI agent that provides a personalized Bible verse based on the user's mood, integrated with Telex.im via A2A Protocol.",
    version="1.0.0"
)

# Pydantic models for the A2A JSON-RPC request/response structure
class A2APart(BaseModel):
    type: str
    text: str

class A2AMessage(BaseModel):
    role: str
    parts: List[A2APart]

class A2AParams(BaseModel):
    message: A2AMessage

class A2ARequest(BaseModel):
    jsonrpc: str
    method: str
    id: Any
    params: A2AParams

class A2AResult(BaseModel):
    role: str
    parts: List[A2APart]
    kind: str = "message"
    message_id: str = "agent_response_id"

class A2AResponse(BaseModel):
    jsonrpc: str
    id: Any
    result: A2AResult

# --- A2A Endpoints ---
@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Returns the Agent Card JSON as required by the A2A protocol."""
    
    return {
        "name": "Daily Bible Verse Agent",
        "description": "Provides a personalized Bible verse based on your mood. Just tell me how you feel!",
        "url": f"{AGENT_BASE_URL}/",
        "version": "1.0.0",
        "provider": {
            "organization": "Your Name/Org",
            "url": "YOUR_ORG_URL"
        },
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": False
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "mood_verse_recommendation",
                "name": "Mood-Based Verse",
                "description": "Generates a relevant Bible verse after analyzing the user's mood description.",
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain"],
                "examples": [
                    {
                        "input": {"parts": [{"type": "text", "text": "I feel anxious and need comfort."}]},
                        "output": {"parts": [{"type": "text", "text": "Fear not, for I am with you; be not dismayed, for I am your God; I will strengthen you, I will help you, I will uphold you with my righteous right hand. (Isaiah 41:10)"}]}
                    }
                ]
            }
        ],
        "supportsAuthenticatedExtendedCard": False
    }

#2. Main A2A Communication Endpoint
@app.post("/")
async def handle_a2a_request(request_body: A2ARequest):
    """Handles incoming JSON-RPC requests from Telex.im."""
    
    if request_body.method == "message/send":
        # Extract user message
        user_message_parts = request_body.params.message.parts
        mood_description = ""
        for part in user_message_parts:
            if part.type == "text":
                mood_description = part.text
                break
        
        if not mood_description:
            response_text = "Please describe your mood so I can find a relevant Bible verse for you."
        else:
            # Get the personalized verse
            verse = get_verse_by_mood(mood_description)
            
            if verse:
                response_text = f"Based on your mood ('{mood_description}'), here is a verse for you:\n\n{verse.text} ({verse.reference})"
            else:
                response_text = "I apologize, I could not find a relevant verse at this time. Please try again later."

        #Construct the A2A Json/RPC Success Response
        response_result = A2AResult(
            role="agent",
            parts=[A2APart(type="text", text=response_text)]
        )
        return A2AResponse(
            jsonrpc="2.0",
            id=request_body.id,
            result=response_result
        )
        
    else:
        # Handle unsupported methods
        return {
            "jsonrpc": "2.0",
            "id": request_body.id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {request_body.method}"
            }
        }

if __name__ == "__main__":
    import uvicorn
    # This is for local testing. When deploying, use a proper server setup.
    uvicorn.run(app, host="0.0.0.0", port=8000)