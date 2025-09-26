# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 🚨 Pydantic v2 Compatibility Error

**Error Message:**
```
pydantic.errors.PydanticUserError: `regex` is removed. use `pattern` instead
```

**Solution:**
This error occurs when using Pydantic v2 with old v1 syntax. The issue has been fixed in the repository.

```bash
# Update to Pydantic v2.5+
pip install 'pydantic>=2.5.0' --upgrade

# Test the fix
python test_pydantic_fix.py

# Or use the setup guide
python setup_guide.py pydantic
```

**What was fixed:**
- ✅ Replaced `regex=` with `pattern=` in Field definitions
- ✅ Updated `@validator` to `@field_validator` with `@classmethod`
- ✅ Updated requirements.txt to specify Pydantic v2.5+

---

### 🔑 Missing API Keys

**Error Message:**
```
Missing GEMINI_API_KEY_4 (or GEMINI_API_KEY) in .env
```

**Solution:**
```bash
# Create .env file from template
python setup_guide.py env

# Edit .env file and add your Gemini API keys
GEMINI_API_KEY=your_primary_key
GEMINI_API_KEY_1=your_auth_key
GEMINI_API_KEY_2=your_behavior_key
GEMINI_API_KEY_3=your_domain_key
GEMINI_API_KEY_4=your_pdf_key
```

**Get Gemini API Keys:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API keys
3. Copy keys to `.env` file

---

### 📄 No PDF Files Found

**Error Message:**
```
🚨 No PDF files found! Please upload requirement documents to the data/ folder first.
```

**Solution:**
```bash
# Check if data directory exists
ls -la data/

# The repository includes 9 sample PDFs:
# Requirement-1.pdf, Requirement-2.pdf, etc.

# If missing, you can add your own PDFs:
cp your-requirements.pdf data/

# Validate PDF files
python setup_guide.py validate
```

---

### 🌐 Kroki Diagram Rendering Issues

**Error Message:**
```
requests.exceptions.ConnectionError: Failed to connect to Kroki
```

**Solutions:**

**Option 1: Check Internet Connection**
```bash
# Test Kroki connectivity
curl -X POST https://kroki.io/mermaid/svg -d "graph TD; A-->B"
```

**Option 2: Use Local MMDC Renderer**
```bash
# Install Mermaid CLI locally
npm install -g @mermaid-js/mermaid-cli

# In Streamlit app, select "mmdc" as renderer
```

**Option 3: Use Custom Kroki Server**
```bash
# In .env file, set custom Kroki URL
KROKI_URL=https://your-kroki-server.com
```

---

### 🐍 Python Version Issues

**Error Message:**
```
❌ Python 3.8+ is required
```

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.8+ if needed
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.8 python3.8-pip

# On macOS with Homebrew:
brew install python@3.8

# On Windows: Download from python.org
```

---

### 📦 Missing Dependencies

**Error Message:**
```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific missing packages
pip install langgraph langchain-core langchain-google-genai

# Check installation
python setup_guide.py check
```

---

### 🔄 LangGraph Workflow Errors

**Error Message:**
```
Workflow execution failed: ...
```

**Debugging Steps:**

1. **Check System Status:**
```bash
python setup_guide.py check
```

2. **Validate PDF Files:**
```bash
python setup_guide.py validate
```

3. **Test Individual Components:**
```bash
python test_pydantic_fix.py
python validate_setup.py
```

4. **Use Sequential Workflow:**
   - In Streamlit app, select "Sequential" workflow type
   - This provides better error isolation

5. **Check Logs:**
   - Look at Streamlit console output
   - Check for specific agent failures

---

### 🎨 Streamlit UI Issues

**Error Message:**
```
streamlit: command not found
```

**Solution:**
```bash
# Install Streamlit
pip install streamlit

# Verify installation
streamlit --version

# Run the app
streamlit run main.py
```

**Port Already in Use:**
```bash
# Use different port
streamlit run main.py --server.port 8502
```

---

### 💾 File Permission Issues

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: 'output/...'
```

**Solution:**
```bash
# Create output directory with proper permissions
mkdir -p output
chmod 755 output

# On Windows, run as administrator if needed
```

---

### 🔍 Debugging Tips

1. **Enable Debug Mode:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Test Individual Agents:**
```python
from agent import PDFExtractionAgent
agent = PDFExtractionAgent()
# Test with sample data
```

3. **Check State Management:**
```python
from state.models import HLDState
state = HLDState(pdf_path="test.pdf")
print(state.dict())
```

4. **Validate Configuration:**
```python
from state.schema import ConfigSchema
config = ConfigSchema()
print(config.dict())
```

---

### 📞 Getting Help

If you're still experiencing issues:

1. **Run Full System Check:**
```bash
python setup_guide.py check
```

2. **Check GitHub Issues:**
   - [Repository Issues](https://github.com/Amruth22/DesignMind_GenAI_LangGraph/issues)

3. **Create New Issue:**
   - Include error messages
   - Include system information
   - Include steps to reproduce

4. **Community Support:**
   - [GitHub Discussions](https://github.com/Amruth22/DesignMind_GenAI_LangGraph/discussions)

---

### ✅ Quick Health Check

Run this command to verify everything is working:

```bash
# Comprehensive system check
python setup_guide.py check

# Quick validation
python validate_setup.py

# Test Pydantic compatibility
python test_pydantic_fix.py
```

If all tests pass, you're ready to run:
```bash
streamlit run main.py
```