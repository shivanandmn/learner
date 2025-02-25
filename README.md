# AI-Powered Educational Assessment Generator

This project helps understand students better by automatically generating questions from educational content. It specifically processes 5th-grade geography content and generates medium-level questions from various subtopics.

## Features
- PDF text extraction using PyPDF2
- Content processing using Microsoft's Markitdown
- Subtopic extraction using LLM
- Automatic question generation based on identified subtopics

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
MARKITDOWN_API_KEY=your_markitdown_api_key
```

3. Place your PDF file in the project directory and update the `pdf_path` in `main.py`

## Usage

Run the main script:
```bash
python main.py
```

This will:
1. Process your PDF file
2. Extract subtopics
3. Generate 10 medium-level questions from random subtopics

## Project Structure
- `pdf_processor.py`: Handles PDF processing and Markitdown integration
- `topic_extractor.py`: Manages topic extraction and question generation
- `main.py`: Main script to run the application
- `requirements.txt`: Project dependencies
