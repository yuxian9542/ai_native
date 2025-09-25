# 🚀 Quick Start Guide

## 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment template
cp env_template.txt .env

# 3. Edit .env with your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here

# 4. Start Elasticsearch (make sure it's running on localhost:9200)

# 5. Load some documents
python pipeline.py --pdf document.pdf --load-only

# 6. Start asking questions!
python pipeline.py --interactive
```

## Essential Commands

```bash
# Check system status
python pipeline.py --status

# Load documents (choose one):
python pipeline.py --pdf document.pdf --load-only          # Single file
python pipeline.py --pdf-dir documents/ --load-only        # Whole directory
python pipeline.py --pdf doc1.pdf --pdf-dir docs/ --load-only  # Mixed

# Ask questions (choose one):
python pipeline.py --interactive                           # Interactive mode
python pipeline.py --pdf doc.pdf --query "Your question"   # One-time query
```

## What This Does

✅ **Extracts** text, images, and tables from PDFs  
✅ **Chunks** content intelligently  
✅ **Vectorizes** everything with embeddings  
✅ **Indexes** to Elasticsearch  
✅ **Searches** with hybrid BM25 + vector search  
✅ **Ranks** results with RRF + reranker  
✅ **Generates** answers with citations  
✅ **Supports** interactive multi-turn conversations  

## That's It! 🎉

For detailed documentation, see [README.md](README.md).
