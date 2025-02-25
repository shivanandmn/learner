import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List, Tuple
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

class TopicExtractor:
    def __init__(self):
        load_dotenv()
        # Configure the Gemini API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_topics_and_subtopics(self, content) -> List[Tuple[str, List[str]]]:
        """Extract topics and their subtopics from the content using Gemini"""
        prompt = f"""
        You are a helpful educational content analyzer. Analyze the following content and:
        1. Identify main topics and their subtopics
        2. Format the response as a JSON string with the following structure:
        {{
            "topics": [
                {{
                    "topic": "Main Topic Name",
                    "subtopics": ["Subtopic 1", "Subtopic 2", ...]
                }}
            ]
        }}
        
        Content: {content}
        """
        
        response = self.model.generate_content(prompt)
        for _ in range(2):
            try:
                topics_data = JsonOutputParser().parse(response.text)
                return [(topic['topic'], topic['subtopics']) for topic in topics_data['topics']]
            except json.JSONDecodeError:
                # Fallback in case the response isn't proper JSON
                prompt  = """Your task is to correct the given below json incorrect formatted json.\n{response.text}"""
                response = self.model.generate_content(prompt)
            return [("Main Topic", [response.text])]

    def generate_questions(self, topic: str, subtopics: List[str], difficulty="medium", num_questions=10) -> List[Dict[str, str]]:
        """Generate questions based on subtopics"""
        prompt = f"""
        You are a helpful educational short question generator for 5th grade. Create engaging and appropriate-level questions.
        Generate {num_questions} {difficulty}-level questions about {topic} based on these subtopics:
        {', '.join(subtopics)}
        You must generate Multiple-choice questions (MCQ) with one being correct answer.
        Correct option index should be provide, index should start from 0 to till 3.

        Format the response as a JSON string with the following structure:
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "answer": ["option 1", "option2", "option 3", "option 4"]
                    "correct_option_index: 0
                }}
            ]
        }}
        """
        
        response = self.model.generate_content(prompt)
        for _ in range(2):
            try:
                questions_data = JsonOutputParser().parse(response.text)
                return questions_data['questions']
            except json.JSONDecodeError or OutputParserException:
                # Fallback in case the response isn't proper JSON
                prompt  = """Your task is to correct the given below json incorrect formatted json.\n{response.text}"""
                response = self.model.generate_content(prompt)
        return [{"question": "Error generating questions", "answer": "Please try again"}]
