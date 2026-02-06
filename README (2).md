# WormAI API 🤖

A deployable AI API inspired by WormGPT - uncensored, fast, and privacy-focused.

## Features

- ✅ **Uncensored Responses** - No content restrictions
- ✅ **Auto-install Dependencies** - Just run `python ai.py`
- ✅ **Render Free Tier Compatible** - Deploy for free
- ✅ **Simple JSON API** - Easy to integrate
- ✅ **Privacy Focused** - No data logging

## Quick Start (Local)

```bash
# Just run the file - it auto-installs dependencies!
python ai.py
```

Then open: http://localhost:5000/?ask=Hello

## API Usage

### Main Endpoint
```
GET /?ask=Your question here
```

**Response:**
```json
{
  "answer": "Hello! How can I assist you today?",
  "model": "WormAI",
  "status": "success"
}
```

### Chat Endpoint
```
GET /chat?message=Your message here
```

### Health Check
```
GET /health
```

### API Info
```
GET /info
```

## Deploy to Render (Free)

### Option 1: Using render.yaml (Recommended)
1. Fork/upload this repo to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml`

### Option 2: Manual Deploy
1. Create a new Web Service on Render
2. Select "Python" environment
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn ai:app --bind 0.0.0.0:$PORT`
5. Choose **Free** plan
6. Deploy!

## Optional: Hugging Face API Key

For better performance, add your free Hugging Face API key:

1. Get free API key at: https://huggingface.co/settings/tokens
2. Add as environment variable `HF_API_KEY` in Render dashboard

## Example Requests

```bash
# Basic question
curl "https://your-app.onrender.com/?ask=Hello"

# Complex query
curl "https://your-app.onrender.com/?ask=Explain quantum computing"

# Chat endpoint
curl "https://your-app.onrender.com/chat?message=How are you?"
```

## Python Example

```python
import requests

response = requests.get("https://your-app.onrender.com/?ask=Hello")
data = response.json()
print(data['answer'])
```

## JavaScript Example

```javascript
fetch('https://your-app.onrender.com/?ask=Hello')
  .then(res => res.json())
  .then(data => console.log(data.answer));
```

## How It Works

1. Uses **Hugging Face Inference API** with open-source models (Mistral-7B, Gemma-2B)
2. Falls back to local responses if API is unavailable
3. No API key required (but recommended for better performance)
4. Runs on Flask with Gunicorn for production

## Models Used

- **Primary:** mistralai/Mistral-7B-Instruct-v0.2
- **Fallback:** google/gemma-2b-it

## Files

- `ai.py` - Main application (auto-installs dependencies)
- `requirements.txt` - Python dependencies
- `render.yaml` - Render deployment config
- `README.md` - This file

## License

MIT - Use freely!
