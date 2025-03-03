from crewai import Agent, Task, Crew
from custom_llm import GeminiLLM
from dotenv import load_dotenv
import os
from typing import List, Dict

class QuestionGeneratorCrew:
    def __init__(self):
        load_dotenv()
        self.llm = GeminiLLM(
            model="gemini/gemini-1.5-flash",
            temperature=0.7,
            api_key=os.getenv('GOOGLE_API_KEY')
        )

    def create_agents(self):
        # Topic Analysis Agent
        topic_analyst = Agent(
            role='Topic Analysis Expert',
            goal='Analyze topics and create detailed context for question generation',
            backstory="""You are an expert in analyzing educational topics and creating 
            comprehensive context for question generation. You have years of experience in 
            breaking down complex topics into manageable learning objectives. """,
            allow_delegation=True,
            llm=self.llm
        )

        # Question Creator Agent
        question_creator = Agent(
            role='Question Generation Specialist',
            goal='Create high-quality educational questions',
            backstory="""You are a specialist in creating engaging and effective educational 
            questions. You have extensive experience in crafting questions that test 
            understanding while maintaining student engagement.""",
            allow_delegation=True,
            llm=self.llm
        )

        # Quality Assurance Agent
        qa_specialist = Agent(
            role='Educational QA Specialist',
            goal='Ensure questions meet educational standards and are error-free',
            backstory="""You are a meticulous educational quality assurance specialist 
            with years of experience in reviewing and improving educational content.""",
            allow_delegation=True,
            llm=self.llm
        )

        return topic_analyst, question_creator, qa_specialist

    def generate_questions(self, complete_chapter, topic: str, subtopics: List[str], difficulty="medium", num_questions=10) -> List[Dict[str, str]]:
        # Create agents
        topic_analyst, question_creator, qa_specialist = self.create_agents()

        # Create tasks
        task1 = Task(
            description=f"""Analyze the topic '{topic}' and its subtopics: {', '.join(subtopics)}. 
            For the below chapter:
            {complete_chapter}
            Create a detailed context and learning objectives for question generation. 
            Consider the difficulty level: {difficulty}.""",
            expected_output="A detailed analysis of the topic and subtopics with clear learning objectives for question generation.",
            agent=topic_analyst
        )

        task2 = Task(
            description=f"""Using the analysis, create {num_questions} multiple-choice questions.
            Each question should:
            1. Be at {difficulty} difficulty level
            2. Have 4 options with exactly one correct answer
            3. Include the correct answer index (0-3)
            Format as JSON: {{"questions": [{{"question": "text", "answer": ["opt1", "opt2", "opt3", "opt4"], "correct_option_index": 0}}]}}""",
            expected_output="A JSON structure containing multiple-choice questions with options and correct answers.",
            agent=question_creator
        )

        task3 = Task(
            description="""Review and improve the generated questions. Ensure:
            1. Question prompt is clear, unambiguous and logically related to context of the topic or subtopic selected.
            2. All answer choices are plausible and relate to the question prompt
            3. There is only one correct answer that unambiguously answers the question, the remaining 3 options cannot answer the question
            4. Validate that the correct answer choice is the single best answer, logically linked to and actually answers the question
            5. Questions are at the appropriate difficulty level
            6. The answer choices should be logically correct. 
            7. JSON format is maintained
            """,
            expected_output="A validated and improved set of questions in JSON format with verified correct answers and appropriate difficulty levels.",
            agent=qa_specialist
        )

        # Create and run the crew
        crew = Crew(
            agents=[topic_analyst, question_creator, qa_specialist],
            tasks=[task1, task2, task3],
            verbose=True
        )

        result = crew.kickoff()
        
        try:
            # Extract the JSON part from the result
            import json
            import re
            
            # Find JSON-like structure in the text
            json_match = re.search(r'\{.*\}', result.raw, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                return questions_data['questions']
            else:
                return [{"question": "Error parsing questions", "answer": ["Please try again"], "correct_option_index": 0}]
        except Exception as e:
            return [{"question": f"Error generating questions: {str(e)}", "answer": ["Please try again"], "correct_option_index": 0}]
