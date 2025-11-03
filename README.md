"""Daily Bible Verse Agent for Telex.im

This project implements an intelligent AI agent in Python that integrates with the Telex.im platform using the Agent-to-Agent (A2A) Protocol. The agent provides a personalized Bible verse recommendation based on the user's current mood."""

## 🌟 Features

*   **Mood-Based Verse Selection:** Uses an LLM (GPT-4.1-mini) to analyze a user's mood description and translate it into spiritual themes/keywords.
*   **A2A Protocol Compliant:** Implements the required Agent Card (`/.well-known/agent.json`) and JSON-RPC communication endpoint (`POST /`).
*   **FastAPI Backend:** Built with Python's FastAPI for high performance and robust data validation using Pydantic.
*   **Local Data Source:** Uses a pre-processed local JSON file of the King James Version (KJV) Bible for fast, reliable verse retrieval.

## 🛠️ Technical Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Web Framework** | Python (FastAPI) | Handles the web server and API endpoints. |
| **AI Logic** | OpenAI API (GPT-4.1-mini) | Semantic analysis of user mood to generate search keywords. |
| **Data Validation** | Pydantic | Ensures strict adherence to the A2A JSON-RPC structure. |
| **Integration** | A2A Protocol (JSON-RPC 2.0) | Standardized communication with Telex.im. |
| **Data** | KJV Bible (JSON) | Local, pre-processed database of all verses. |

## 🚀 Getting Started

Follow these steps to set up and run the agent locally before deployment.

### Prerequisites

1.  Python 3.8+
2.  An OpenAI API Key
3.  `git` and `pip` installed

### Step 1: Clone the Repository and Setup Environment

Assuming you have cloned this project into a directory named `telex-bible-agent`:

```bash
cd telex-bible-agent

# Create and activate a virtual environment (Recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

### Step 2: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### Step 3: Prepare the Bible Data

The agent requires two data files: `bible_data.json` (raw) and `processed_bible_data.json` (flattened).

1.  **Download the raw data:**
    ```bash
    # If you have wget:
    wget https://raw.githubusercontent.com/scrollmapper/bible_databases/master/formats/json/KJV.json -O bible_data.json
    
    # If you are on macOS and prefer curl:
    curl -o bible_data.json https://raw.githubusercontent.com/scrollmapper/bible_databases/master/formats/json/KJV.json
    ```

2.  **Run the pre-processor:**
    ```bash
    python bible_processor.py
    ```
    This will create the `processed_bible_data.json` file.

### Step 4: Run the Agent Locally

1.  **Set the OpenAI API Key** as an environment variable. Replace `YOUR_API_KEY` with your actual key.

    ```bash
    export OPENAI_API_KEY="YOUR_API_KEY"
    ```

2.  **Start the FastAPI server** using Uvicorn. For local testing, we use port 8000.

    ```bash
    uvicorn bible_agent:app --host 0.0.0.0 --port 8000
    ```

The agent is now running locally at `http://localhost:8000`.

## 🌐 Deployment and Telex.im Integration

For Telex.im to communicate with your agent, it **must** be deployed to a public URL.

### 1. Deployment

Choose a hosting service (e.g., Render, Heroku, AWS) and deploy your application.

*   **Build Command:** `pip install -r requirements.txt`
*   **Start Command:** `uvicorn bible_agent:app --host 0.0.0.0 --port $PORT`
*   **Environment Variable:** Set `OPENAI_API_KEY` to your secret key.

### 2. Update `AGENT_BASE_URL`

Once deployed, the hosting service will give you a public URL (e.g., `https://my-bible-agent.com`). You must update the `AGENT_BASE_URL` variable inside `bible_agent.py` with this URL and redeploy.

### 3. Connect to Telex.im

The final URL you provide to Telex.im is the **Agent Card URL**:

```
[YOUR_PUBLIC_URL]/.well-known/agent.json
```

Paste this URL into the Telex.im Integrations/Agents section to connect your agent.

## 💡 Usage

Once connected to Telex.im, users can interact with the agent by mentioning it and describing their mood:

**Example Input:**
`@Daily Bible Verse Agent I'm feeling anxious and worried about the future.`

**Example Output:**
`Based on your mood ('I'm feeling anxious and worried about the future.'), here is a verse for you: Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God. (Philippians 4:6)`

## 📄 Project Files
