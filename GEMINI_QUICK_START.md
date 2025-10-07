# 🚀 Quick Start: Using Gemini API (FREE!)

## Why Gemini?
- ✅ **100% FREE** - No credit card required
- ✅ **Higher limits** than OpenAI free tier  
- ✅ **1,500 requests/day** - Perfect for development
- ✅ **Good quality** - Comparable to GPT-3.5/4o-mini

---

## Step 1: Get Your FREE Gemini API Key (2 minutes)

1. **Visit**: https://aistudio.google.com/app/apikey
2. **Sign in** with your Google account
3. Click **"Create API key"**
4. **Copy** the key (starts with `AIza...`)

**That's it!** No credit card, no billing setup needed. 🎉

---

## Step 2: Update Your `.env` File

Open `/Users/achyuthansivasankar/PROJECTS/rag-knowledge-base/.env` and update:

```bash
# Replace this line:
GEMINI_API_KEY=your_gemini_api_key_here

# With your actual key:
GEMINI_API_KEY=AIzaSy...your_actual_key
```

The file should already have these settings (no changes needed):
```bash
LLM_PROVIDER=gemini
EMBEDDING_MODEL=models/text-embedding-004
EMBEDDING_DIMENSION=768
LLM_MODEL=gemini-1.5-flash
```

---

## Step 3: Test Your Setup

```bash
cd /Users/achyuthansivasankar/PROJECTS/rag-knowledge-base

# Test Gemini connection
./.venv/bin/python scripts/test_gemini.py
```

You should see:
```
✅ Embedding generated successfully!
✅ LLM response received!
✅ ALL TESTS PASSED!
```

---

## Step 4: Run the System

### Terminal 1 - Start API Server:
```bash
cd /Users/achyuthansivasankar/PROJECTS/rag-knowledge-base
./.venv/bin/uvicorn api.main:app --reload --port 8000
```

### Terminal 2 - Start UI:
```bash
cd /Users/achyuthansivasankar/PROJECTS/rag-knowledge-base
./.venv/bin/streamlit run ui/app.py
```

### Terminal 3 - Load Sample Data:
```bash
cd /Users/achyuthansivasankar/PROJECTS/rag-knowledge-base
./.venv/bin/python scripts/ingest_sample_data.py
```

---

## Access Points

- **API Docs**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501  
- **Neo4j Browser**: http://localhost:7474 (user: `neo4j`, pass: `password123`)

---

## Important: Clear Old Data

If you previously used OpenAI embeddings, you need to clear the vector store (different embedding dimensions):

```bash
rm -rf /Users/achyuthansivasankar/PROJECTS/rag-knowledge-base/data/chroma_db
```

Then re-ingest your documents.

---

## Switching Between OpenAI and Gemini

Just change one line in `.env`:

**For Gemini (FREE):**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...
EMBEDDING_MODEL=models/text-embedding-004
EMBEDDING_DIMENSION=768
LLM_MODEL=gemini-1.5-flash
```

**For OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
LLM_MODEL=gpt-4o-mini
```

Restart the services after changing.

---

## Troubleshooting

### "GEMINI_API_KEY not set"
- Make sure you edited the `.env` file (not `.env.example`)
- Remove quotes around the API key
- Restart the application

### "Embedding dimension mismatch"
- Clear ChromaDB: `rm -rf ./data/chroma_db`
- Make sure `EMBEDDING_DIMENSION=768` in `.env`

### "Rate limit exceeded"
- Free tier: 15 requests/minute, 1500/day
- Add delays between requests or upgrade at https://ai.google.dev/pricing

---

## What Changed?

✅ **Modified Files:**
1. `config/settings.py` - Added Gemini support
2. `src/llm/client.py` - Multi-provider LLM client
3. `src/ingestion/embedder.py` - Multi-provider embeddings
4. `.env` - Added Gemini configuration
5. Added `google-generativeai` package

✅ **New Files:**
1. `GEMINI_SETUP.md` - Detailed guide
2. `scripts/test_gemini.py` - Connection test
3. `GEMINI_QUICK_START.md` - This file

---

## Next Steps

1. ✅ Get API key from https://aistudio.google.com/app/apikey
2. ✅ Update `.env` with your key
3. ✅ Run `test_gemini.py` to verify
4. ✅ Start the API and UI
5. ✅ Ingest some documents
6. ✅ Start querying!

**Need help?** Check `GEMINI_SETUP.md` for detailed information.

---

**Your RAG system now has FREE, unlimited-ish access to AI! 🎉**
