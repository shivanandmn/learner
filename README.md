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

---------------------------------------------------------------------------------------------------

Difficulty level metrics:

1. Cognitive Load Metric
Definition:
Cognitive load refers to the amount of mental effort required to understand, process, and answer a question. It captures the complexity of the reasoning involved and the depth of understanding needed.

Scoring Scale (1–5):

1: Very low effort required (simple recall or recognition)
2: Low effort (basic comprehension)
3: Moderate effort (requires some analysis or inference)
4: High effort (involves multi-step reasoning or integration of multiple pieces of information)
5: Extremely high effort (requires complex reasoning, synthesis, or deep conceptual understanding)
Example:

Question: "Which animal uses pheromones to communicate and navigate?"
Cognitive Load Rating: 2 (The question requires recall of a known fact with minimal processing.)
Alternate Question: "How do ants utilize chemical signals to coordinate complex colony behaviors?"
Cognitive Load Rating: 4 (This version requires understanding of multiple concepts and deeper reasoning.)
2. Lexical Complexity Metric
Definition:
Lexical complexity evaluates the difficulty of the language used in the question. It takes into account vocabulary sophistication, word frequency, sentence length, and overall readability.

Scoring Scale (1–5):

1: Very simple language (common words, short sentences, high readability)
2: Simple language with minor complexity
3: Moderate complexity (some less common words, moderately long sentences)
4: High complexity (advanced vocabulary, longer and more compound sentences)
5: Extremely high complexity (sophisticated vocabulary, complex syntactic structures, low readability)
Example:

Question: "What is the primary method ants use to communicate?"
Lexical Complexity Rating: 2 (Uses simple, common vocabulary and straightforward structure.)
Alternate Question: "In what manner do ants deploy pheromonal signals to orchestrate their foraging activities?"
Lexical Complexity Rating: 5 (Involves advanced vocabulary like “deploy,” “phermonal signals,” and “orchestrate,” with a complex sentence structure.)
3. Question Structure Metric
Definition:
The question structure metric assesses how a question is constructed. It considers clarity, logical flow, the number of steps or layers needed to arrive at the answer, and the effectiveness of distractor options.

Scoring Scale (1–5):

1: Very straightforward (one-step, clear question with minimal distractors)
2: Simple structure (clear wording, minimal additional steps)
3: Moderately complex (requires one or two steps of reasoning, with plausible distractors)
4: Complex (multiple steps of reasoning or inference needed, with several strong distractors)
5: Very complex (ambiguous or multi-layered question structure that challenges reasoning significantly)
Example:

Question: "Which animal is known for its exceptional night vision?"
Question Structure Rating: 2 (A direct, clear question with obvious distractors.)
Alternate Question: "Which of the following factors most significantly contributes to the superior nocturnal vision of tigers?"
Question Structure Rating: 4 (Requires interpretation of how different factors contribute, with distractors that may seem plausible.)
