import json
import random
from typing import Dict, List, Any

class DataManager:
    def __init__(self, output_file: str = "output/content.json"):
        self.output_file = output_file
        self.data = {
            "topics": {},  # Will store all topics and their subtopics
            "selected_topics": [],  # Will store 10 randomly selected topics with questions
            "prerequisites": {},  # Will store prerequisite relationships and learning sequence
        }
    
    def add_topic(self, topic: str, subtopics: List[str]):
        """Add a topic and its subtopics to the data structure"""
        if topic not in self.data["topics"]:
            self.data["topics"][topic] = {
                "subtopics": subtopics,
                "questions": []
            }
    
    def add_questions(self, topic: str, questions: List[Dict[str, str]]):
        """Add questions to a specific topic"""
        if topic in self.data["topics"]:
            self.data["topics"][topic]["questions"].extend(questions)
    
    def select_random_topics(self, num_topics: int = 10) -> List[str]:
        """Select random topics for question generation"""
        available_topics = list(self.data["topics"].keys())
        num_to_select = min(num_topics, len(available_topics))
        return random.sample(available_topics, num_to_select)
    
    def prepare_selected_topics(self):
        """Prepare the selected topics with their questions"""
        selected_topics = self.select_random_topics()
        self.data["selected_topics"] = []
        
        for topic in selected_topics:
            topic_data = self.data["topics"][topic]
            self.data["selected_topics"].append({
                "topic": topic,
                "subtopics": topic_data["subtopics"],
                "questions": topic_data["questions"]
            })
    
    def add_prerequisites(self, prerequisite_data: Dict):
        """Add prerequisite relationships and learning sequence to the data structure"""
        self.data["prerequisites"] = prerequisite_data

    def save_to_json(self):
        """Save the data structure to a JSON file"""
        # Ensure the output directory exists
        import os
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self) -> Dict[str, Any]:
        """Load data from the JSON file"""
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return self.data
        except FileNotFoundError:
            return self.data
