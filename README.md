# LLM_Task
It's a full-stack application that processes user text to identify and highlight Personally Identifiable Information (PII) before generating a paraphrased version using a local Large Language Model.

Link to Screenshot:-
https://drive.google.com/file/d/1SFZ1a-s3h3y6ygyupUd12ZuKFRbDYYZj/view?usp=drivesdk
https://drive.google.com/file/d/1kiD1dtZ97i-2_Ej1CoYgMmtwewafJspk/view?usp=drivesdk
                  

## Features

- **FastAPI Backend**: A robust and modern API server.
- **Named Entity Recognition (NER)**: Uses **spaCy** to accurately detect entities like names and locations.
- **Local LLM Integration**: Connects to a locally-hosted LLM via **Ollama**'s REST API.
- **Interactive UI**: A dynamic frontend that communicates with the backend to display results without a page reload.
- **PII Highlighting (Bonus)**: Visually highlights detected entities in the original prompt for clarity.



- **Backend**: Python, FastAPI
- **LLM Engine**: Ollama (configured for `phi3:latest`)
- **NLP Library**: spaCy (`en_core_web_sm`)
- **Frontend**: HTML, CSS, Vanilla JavaScript


**Prerequisites:**
- Python 3.8+
- [Ollama](https://ollama.com/) installed and running.

ollama pull phi3
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate    # On Windows

# Install required packages
pip install -r requirements.txt

Start the FastAPI backend server using Uvicorn
uvicorn backend.main:app --reload

Project Structure
.
├── backend/
│   └── main.py         # FastAPI application with all API logic
├── frontend/
│   ├── index.html      # Main application UI
│   └── script.js       # JavaScript for API calls and UI updates
├── .gitignore          # Specifies files for Git to ignore
├── README.md           # You are here!
└── requirements.txt    # Python dependencies

-------------Console Output Example--------

--- Detected Named Entities (spaCy) ---
[{'text': 'John Doe', 'label': 'PERSON'}, {'text': 'Dublin, CA', 'label': 'GPE'}]

--- Response from LLM (Ollama) ---
John Doe resides in the city of Dublin, California.
