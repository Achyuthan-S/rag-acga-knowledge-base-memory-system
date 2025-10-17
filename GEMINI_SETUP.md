# Google Gemini API Setup Guide

## Why Use Gemini?

✅ **FREE Tier Benefits:**
- 15 requests per minute (RPM)
- 1 million tokens per minute (TPM)  
- 1,500 requests per day
- **No credit card required!**

✅ **Advantages:**
- Higher rate limits than OpenAI free tier
- Fast and efficient (Gemini 1.5 Flash is optimized for speed)
- Good quality embeddings (768 dimensions)
- Free for personal projects

## Get Your Free Gemini API Key

### Step 1: Visit Google AI Studio
Go to: https://aistudio.google.com/app/apikey

### Step 2: Sign In
- Sign in with your Google account
- No credit card needed!

### Step 3: Create API Key
1. Click **"Get API key"** or **"Create API key"**
2. Select **"Create API key in new project"** (or use existing project)
3. Copy your API key (starts with `AIza...`)

### Step 4: Add to Your Project
Edit the `.env` file in your project:

```bash
GEMINI_API_KEY=AIzaSy...your_actual_key_here
LLM_PROVIDER=gemini
```

That's it! No billing setup required.

## Available Models

### For Chat/Generation:
- **gemini-1.5-flash** (Recommended) - Fast, efficient, free
- **gemini-1.5-pro** - More capable, still free but lower limits
- **gemini-2.0-flash-exp** - Latest experimental model

### For Embeddings:
- **models/text-embedding-004** - 768 dimensions, optimized for retrieval

## Rate Limits (Free Tier)

| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| Gemini 1.5 Flash | 15 | 1M | 1,500 |
| Gemini 1.5 Pro | 2 | 32K | 50 |
| Text Embedding | 15 | 1.5M | 1,500 |

RPM = Requests Per Minute, TPM = Tokens Per Minute, RPD = Requests Per Day

## Switching Between Providers

Your RAG system now supports both OpenAI and Gemini!

### Use Gemini (Free):
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...
EMBEDDING_MODEL=models/text-embedding-004
EMBEDDING_DIMENSION=768
LLM_MODEL=gemini-1.5-flash
```

### Use OpenAI:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
LLM_MODEL=gpt-4o-mini
```

Just change `LLM_PROVIDER` in your `.env` file and restart the application!

## Testing Your Setup

After adding your Gemini API key, test it:

```bash
cd /Users/achyuthansivasankar/PROJECTS/rag-knowledge-base

# Test the system
./.venv/bin/python scripts/test_system.py

# Or start the API
./.venv/bin/uvicorn api.main:app --reload --port 8000
```

## Important Notes

⚠️ **Embedding Dimensions Changed:**
- Gemini uses **768 dimensions** (vs OpenAI's 1536)
- If you already have data stored with OpenAI embeddings, you'll need to:
  1. Clear your ChromaDB data: `rm -rf ./data/chroma_db`
  2. Re-ingest your documents with Gemini embeddings

💡 **Tips:**
- Keep your API key secret (don't commit `.env` to git)
- Monitor your usage at: https://aistudio.google.com/app/apikey
- Gemini is great for development and small-to-medium projects
- For production at scale, consider paid tiers

## Resources

- **API Documentation**: https://ai.google.dev/docs
- **Pricing**: https://ai.google.dev/pricing
- **Python SDK**: https://github.com/google/generative-ai-python
- **Get API Key**: https://aistudio.google.com/app/apikey

---

**Ready to use Gemini!** Get your free API key and update the `.env` file. 🚀
