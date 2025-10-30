# Quick Start Guide - DesignMind GenAI LangGraph

## What You Have

A complete system with **3 integrated workflows** for automating HLD generation and quality assessment using LangGraph and Machine Learning.

---

## Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
streamlit run main.py
```

### Step 3: Open in Browser
Navigate to: http://localhost:8501

---

## Three Main Workflows

### 🏗️ TAB 1: HLD GENERATION
**Automatically generate architecture documents from PDF requirements**

1. Click the "HLD Generation" tab
2. Upload PDF files to the `data/` folder
3. Select a requirement PDF
4. Configure workflow type (sequential, parallel, conditional)
5. Click "Generate High-Level Design"
6. Download results (Markdown, HTML, diagrams)

**Output**: Complete HLD with architecture, security, APIs, diagrams

---

### 🤖 TAB 2: ML TRAINING
**Train machine learning models to assess HLD quality**

#### Workflow:
1. Click the "ML Training" tab
2. Click "Generate 30,000 Row Dataset"
   - Creates synthetic dataset with 38 features
   - Generates quality scores for each sample
3. Click "Train ML Models"
   - Trains 3 algorithms: Random Forest, Gradient Boosting, Linear Regression
   - Shows performance metrics
4. Models are saved automatically

**Output**: Trained models ready for predictions

---

### 🔮 TAB 3: QUALITY PREDICTION
**Predict HLD quality using trained models**

#### Three Sub-tabs:

**A) Quick Scenario**
- Select predefined scenario: Excellent/Good/Poor HLD
- Click "Predict Quality Score"
- See predictions from all models

**B) Custom Features**
- Adjust feature sliders (38 features total)
- Customize section checkboxes
- Click "Predict with Custom Features"
- Get ensemble prediction

**C) Feature Guide**
- View all 38 feature descriptions
- See acceptable value ranges
- Understand feature meanings

**Output**: Quality scores from multiple models + ensemble average

---

## Dataset & Model Details

### Features (38 Total)
- **Text Metrics** (4): word_count, sentence_count, sentence length, word length
- **Structure** (5): headers, code blocks, tables, lists, diagrams
- **Semantic** (7): completeness, security, scalability, API, database, performance, monitoring mentions
- **Consistency** (3): duplicate headers, coverage metrics
- **Density** (2): keyword, section density
- **Properties** (7): has architecture, security, scalability, deployment, monitoring, API spec, data model
- **Complexity** (3): service count, entity count, API endpoint count
- **Quality** (4): readability, completeness index, consistency index, documentation quality
- **Text** (2): technical terms density, acronym count

### Models Trained
1. **Random Forest**: 100 trees, max_depth=15
2. **Gradient Boosting**: 100 stages, max_depth=5, learning_rate=0.1 (⭐ Recommended)
3. **Linear Regression**: Simple baseline

### Expected Performance
- **Gradient Boosting** (Best):
  - Test R²: 0.83
  - Prediction error: ±3.23 points

- **Linear Regression** (Fast):
  - Test R²: 0.85
  - Prediction error: ±3.07 points

---

## Command Line Usage

### Generate Dataset
```bash
python -m ml.training.generate_dataset
```

### Train Models
```bash
python -m ml.training.train_large_model
```

### Make Predictions
```bash
python -m ml.training.inference
```

### Score HLD with Rules
```bash
python -m ml.models.quality_scorer
```

---

## Python API Usage

### Extract Features from HLD Text
```python
from ml.models.feature_extractor import FeatureExtractor

extractor = FeatureExtractor()
features = extractor.extract("# My HLD document text...")

print(f"Word count: {features.word_count}")
print(f"Has API spec: {features.has_api_spec}")
print(f"Security mentions: {features.security_mentions}")
```

### Make Predictions
```python
from ml.training.inference import HLDQualityPredictor

predictor = HLDQualityPredictor()
predictor.load_models_from_disk()

features = {
    'word_count': 3000,
    'sentence_count': 250,
    'header_count': 20,
    'has_security_section': 1,
    # ... 34 more features
}

predictions = predictor.predict(features)
print(predictions)
# Output: {'Random Forest': 75.2, 'Gradient Boosting': 78.5, 'ensemble_average': 76.85}
```

### Score with Rule-Based Scorer
```python
from ml.models.quality_scorer import RuleBasedQualityScorer

scorer = RuleBasedQualityScorer()
score = scorer.score("# HLD text...")

print(f"Overall: {score.overall_score}/100")
print(f"Completeness: {score.completeness}/100")
print(f"Recommendations: {score.recommendations}")
```

---

## Quality Score Interpretation

- **85-100**: Excellent - Comprehensive, well-structured HLD
- **70-84**: Good - Complete HLD with minor improvements possible
- **50-69**: Fair - Adequate HLD with room for improvement
- **Below 50**: Poor - Significant improvements needed

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No PDF files found" | Place PDF files in `data/` folder |
| "Models not found" | Generate dataset and train models in ML Training tab |
| "Prediction returns NaN" | Ensure all 38 features are provided with valid values |
| "Out of memory" | Reduce dataset size from 30,000 to 10,000 samples |
| Import errors | Run `pip install -r requirements.txt` |

---

## Directory Structure

```
DesignMind_GenAI_LangGraph/
├── main.py                          # Main Streamlit app
├── requirements.txt                 # Dependencies
├── ml/
│   ├── training/
│   │   ├── generate_dataset.py      # Generate 30K samples
│   │   ├── train_large_model.py     # Train 3 models
│   │   ├── inference.py             # Make predictions
│   │   └── synthetic_hld_dataset.csv # 30K samples
│   └── models/
│       ├── feature_extractor.py     # Extract 38 features
│       ├── ml_quality_model.py      # Model classes
│       └── quality_scorer.py        # Rule-based scoring
├── data/                            # Input PDFs
└── output/                          # Generated HLDs
```

---

## Next Steps

1. **Prepare Data**: Add sample PDFs to `data/` folder
2. **Generate Dataset**: Use ML Training tab
3. **Train Models**: Click "Train ML Models" button
4. **Test Predictions**: Use Quality Prediction tab
5. **Generate HLDs**: Use HLD Generation tab with your requirements

---

## Key Features

✅ **Automated HLD Generation**: From PDF requirements
✅ **ML-Based Quality Assessment**: 3 algorithms, ensemble predictions
✅ **Interactive UI**: Streamlit with 3 integrated tabs
✅ **38-Feature Analysis**: Comprehensive document analysis
✅ **30,000 Synthetic Samples**: For robust model training
✅ **Multiple Output Formats**: Markdown, HTML, diagrams
✅ **Production Ready**: Models persist, predictions cached

---

## Support

For detailed information, see:
- `IMPLEMENTATION_SUMMARY.md` - Complete technical documentation
- `PROBLEM_DESCRIPTION.txt` - Original requirements
- Code comments in individual modules

---

**Ready to go!** 🚀 Start with Tab 1 to generate an HLD, Tab 2 to train models, and Tab 3 to assess quality.
