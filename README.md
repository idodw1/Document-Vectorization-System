# Document Vectorization System

A Python-based system for processing documents, splitting text into chunks, and generating embeddings using Google Gemini API.

---

## 📋 System Overview

The system performs the following operations:
1. **Document Reading** - Supports PDF and DOCX files
2. **Text Splitting** - 3 different chunking strategies
3. **Embedding Generation** - Using Google Gemini API
4. **Statistical Evaluation** - Selects the optimal strategy
5. **Database Storage** - PostgreSQL with vector support

---

## 🔧 System Requirements

### Required Software:
- **Python 3.12** (required - newer versions not supported)
- **PostgreSQL** (database)
- **Google Gemini API Key** (paid account recommended)

### Python Packages:
```
python-dotenv==1.0.0
PyPDF2==3.0.1
python-docx==1.1.0
google-generativeai==0.8.3
psycopg[binary]>=3.1.0
numpy>=1.26.0
scikit-learn>=1.5.0
```

---

## 📥 Installation

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd document_vectorization
```

### Step 2: Create Virtual Environment
```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```

Edit the `.env` file and add your credentials:
```
GEMINI_API_KEY=your_api_key_here
POSTGRES_URL=postgresql://user:password@localhost:5432/dbname
```

**How to get API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API Key
3. Copy and paste into `.env`

### Step 5: Setup Database
```bash
python db_setup.py
```

You should see:
```
============================================================
DATABASE SETUP
============================================================
✓ Database connection successful
✓ Table 'document_chunks' ready

✓ Database setup complete!
```

---

## 🚀 Usage

### Basic Usage:
```bash
python index_documents.py path/to/document.pdf
```

### Examples:
```bash
# Process PDF
python index_documents.py documents/report.pdf

# Process DOCX
python index_documents.py presentation.docx

# Process file from Desktop
python index_documents.py ~/Desktop/file.pdf
```

---

## 📊 Sample Output
```
======================================================================
  DOCUMENT VECTORIZATION PIPELINE
======================================================================
File: test_document.pdf

======================================================================
  STEP 1: READING FILE
======================================================================
✓ Extracted 646 characters from test_document.pdf

======================================================================
  STEP 2: SPLITTING TEXT
======================================================================
1. Fixed Size with Overlap (500 chars, 50 overlap)...
   ✓ Created 2 chunks
2. Sentence-Based Splitting (5 sentences per chunk)...
   ✓ Created 2 chunks
3. Paragraph-Based Splitting (min 100 chars)...
   ✓ Created 1 chunks

======================================================================
  STEP 3: GENERATING EMBEDDINGS
======================================================================
✓ Generated embeddings (dimension: 768)

======================================================================
  STEP 4: EVALUATING STRATEGIES
======================================================================
FIXED SIZE:      Score: 0.706
SENTENCE BASED:  Score: 0.736  🏆 WINNER
PARAGRAPH BASED: Score: 0.700

======================================================================
  STEP 5: SAVING TO POSTGRESQL
======================================================================
✓ Saved 2 chunks with strategy: sentence_based

======================================================================
  SUMMARY
======================================================================
File processed: test_document.pdf
Best strategy: sentence_based
Chunks created: 2
Status: ✓ Processing complete
======================================================================
```

---

## 🏗️ Project Structure
```
document_vectorization/
├── file_reader.py           # PDF/DOCX reading
├── text_splitter.py         # Text chunking strategies
├── embedding_generator.py   # Gemini embedding generation
├── strategy_evaluator.py    # Strategy evaluation
├── database.py              # PostgreSQL operations
├── index_documents.py       # Main script
├── db_setup.py              # Database setup
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Environment variables (not in repo!)
└── README.md                # This documentation
```

---

## 📐 Chunking Strategies

### 1. Fixed Size with Overlap
- Fixed size: 500 characters
- Overlap: 50 characters
- **Best for**: Long documents with continuous flow

### 2. Sentence-Based Splitting
- 5 sentences per chunk
- **Best for**: Text with clear sentence boundaries

### 3. Paragraph-Based Splitting
- Split by paragraphs
- Minimum: 100 characters
- **Best for**: Documents with clear paragraph structure

### Evaluation Criteria:
The system selects the best strategy based on:
- **Coverage** (30%) - How well chunks cover the document
- **Similarity** (30%) - Coherence between chunks
- **Size Consistency** (20%) - Uniformity in chunk sizes
- **Chunk Count** (20%) - Preference for reasonable number of chunks

---

## 🗄️ Database Schema
```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding_vector REAL[] NOT NULL,
    split_strategy VARCHAR(50) NOT NULL,
    chunk_size INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id` - Unique identifier
- `filename` - Source file name
- `chunk_text` - Text content of the chunk
- `chunk_index` - Position in document
- `embedding_vector` - 768-dimensional vector
- `split_strategy` - Selected strategy name
- `chunk_size` - Chunk size in characters
- `created_at` - Creation timestamp

---

## ⚙️ Advanced Configuration

### Adjust Parameters in text_splitter.py:
```python
# Fixed size
chunk_size=500      # Chunk size
overlap=50          # Overlap between chunks

# Sentence-based
sentences_per_chunk=5

# Paragraph-based
min_paragraph_length=100
```

### Adjust Batch Size in embedding_generator.py:
```python
batch_size=10       # Number of embeddings per request
delay=0.5          # Delay between requests (seconds)
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'X'`
**Solution:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: `FileNotFoundError: [Errno 2] No such file or directory`
**Solution:**
- Verify the file path is correct
- Use absolute path: `python index_documents.py /full/path/to/file.pdf`

### Issue: `429 Quota exceeded`
**Solution:**
- Free tier Gemini account is limited
- Upgrade to paid account: [Google AI Pricing](https://ai.google.dev/pricing)

### Issue: `column "X" does not exist`
**Solution:**
```bash
python db_setup.py  # Recreates the table
```

### Issue: Python 3.13/3.14
**Solution:**
```bash
brew install python@3.12
python3.12 -m venv .venv
```

---

## 📊 API Costs

**Google Gemini Embedding API:**
- Free tier: 1,500 requests/day (limited)
- Paid: $0.00001 per request
- Typical document: 3-5 chunks = $0.00003-$0.00005

---

## 🔒 Security

**⚠️ Important:**
- Never share your `.env` file
- Never upload API keys to GitHub
- Use `.gitignore` to prevent this

---

## 📝 License

This project was created for educational purposes.

---

## 👤 Author

**Ido Dwek**  
[GitHub](https://github.com/idodw1) | [LinkedIn](https://linkedin.com/in/idodwek)

---

## 📞 Support

Encountered an issue? Please contact me – Ido – [Whatsapp](https://wa.me/972549059942?text=Hey%20There,%20I%20really%20liked%20your%20Document%20Vectorization%20System!%20but%20I%20do%20have%20a%20question...)


---

**✅ System Ready to Use!**