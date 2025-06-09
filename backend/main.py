import spacy
import requests
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- 1. INITIALIZATION ---

# Initialize FastAPI app
app = FastAPI()

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# --- 2. Pydantic Models for Data Validation ---
# This is a best practice for clean and predictable APIs.

class ProcessRequest(BaseModel):
    prompt: str

class NerResult(BaseModel):
    text: str
    label: str

class ProcessResponse(BaseModel):
    llm_response: str
    named_entities: list[NerResult]
    sanitized_prompt: str

# --- 3. CORS MIDDLEWARE ---
# Allow requests from your frontend (which will be served on a different port/origin during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- 4. CORE LOGIC FUNCTIONS ---

def detect_pii_spacy(text: str) -> list[dict]:
    """Detects named entities using spaCy."""
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    print("--- Detected Named Entities (spaCy) ---")
    print(entities)
    return entities

def get_llm_response(prompt: str) -> str:
    """Gets a response from the local Ollama LLM."""
    payload = {
        "model": "phi3",  # Or "llama3:8b", whichever you downloaded
        "prompt": prompt,
        "stream": False  # As per instructions, no streaming needed
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # The response from Ollama is a JSON object
        response_data = response.json()
        llm_response = response_data.get("response", "Error: No response field in LLM output.")
        
        print("--- Response from LLM (Ollama) ---")
        print(llm_response)
        return llm_response

    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        return "Error: Could not connect to the local LLM."

def sanitize_prompt(prompt: str, entities: list[dict]) -> str:
    """Replaces detected PII with their labels for 'sanitization'."""
    sanitized_text = prompt
    for entity in entities:
        sanitized_text = sanitized_text.replace(entity["text"], f"[{entity['label']}]")
    return sanitized_text


# --- 5. API ENDPOINT ---

@app.post("/process", response_model=ProcessResponse)
async def process_prompt(request: ProcessRequest):
    """
    Main endpoint to process a user prompt.
    1. Detects PII/NER.
    2. Sanitizes the prompt (for demonstration).
    3. Sends the *original* prompt to the LLM.
    4. Returns LLM response and detected entities.
    """
    prompt = request.prompt
    
    # Step 1: Detect Named Entities
    entities = detect_pii_spacy(prompt)
    
    # Step 2: Sanitize the prompt (as shown in the UI screenshot)
    sanitized_text = sanitize_prompt(prompt, entities)
    
    # The challenge says "Paraphrase this:", so let's send the full prompt to the LLM.
    llm_prompt = f"Paraphrase the following sentence: '{prompt}'"
    
    # Step 3: Get response from the LLM
    llm_answer = get_llm_response(llm_prompt)
    
    return ProcessResponse(
        llm_response=llm_answer,
        named_entities=entities,
        sanitized_prompt=sanitized_text
    )

# --- 6. SERVE FRONTEND (Bonus Points) ---

# Mount the 'frontend' directory to serve static files like JS and CSS
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_root():
    """Serves the main HTML file."""
    return FileResponse('frontend/index.html')