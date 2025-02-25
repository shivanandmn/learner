from crewai import Agent, Task, Crew
from custom_llm import GeminiLLM
from dotenv import load_dotenv
import os
import json
import networkx as nx
from networkx.readwrite import write_gexf, read_gexf
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple

class PrerequisiteAnalyzer:
    def __init__(self, graphs_dir: str = "output/graphs"):
        load_dotenv()
        self.llm = GeminiLLM(
            model="gemini/gemini-1.5-flash",
            temperature=0.7,
            api_key=os.getenv('GOOGLE_API_KEY')
        )
        self.graphs_dir = graphs_dir
        os.makedirs(self.graphs_dir, exist_ok=True)
        
        # Try to load existing graphs, or create new ones if they don't exist
        self.load_or_create_graphs()

    def create_agents(self):
        # Content Analysis Expert
        content_analyst = Agent(
            role='Content Analysis Expert',
            goal='Analyze textbook content and identify topic relationships',
            backstory="""You are an expert in educational content analysis with deep 
            understanding of how concepts build upon each other. You excel at identifying 
            prerequisite relationships between topics.""",
            allow_delegation=True,
            llm=self.llm
        )

        # Prerequisite Relationship Expert
        relationship_expert = Agent(
            role='Prerequisite Relationship Expert',
            goal='Define and validate prerequisite relationships between topics',
            backstory="""You are a specialist in determining educational prerequisites 
            and dependencies. You understand how knowledge builds sequentially and can 
            identify when one topic is necessary to understand another.""",
            allow_delegation=True,
            llm=self.llm
        )

        # Educational Sequence Specialist
        sequence_specialist = Agent(
            role='Educational Sequence Specialist',
            goal='Organize topics into optimal learning sequences',
            backstory="""You are an expert in curriculum design and learning sequences. 
            You understand how to arrange topics to optimize learning and ensure students 
            have necessary foundational knowledge.""",
            allow_delegation=True,
            llm=self.llm
        )

        return content_analyst, relationship_expert, sequence_specialist

    def load_or_create_graphs(self):
        """Load existing graphs from files or create new ones"""
        try:
            # Load subtopic graph
            self.subtopic_graph = read_gexf(os.path.join(self.graphs_dir, 'subtopic_graph.gexf'))
            # Load topic graph
            self.topic_graph = read_gexf(os.path.join(self.graphs_dir, 'topic_graph.gexf'))
            # Load subtopic to topic mapping
            with open(os.path.join(self.graphs_dir, 'subtopic_to_topic.json'), 'r') as f:
                self.subtopic_to_topic = json.load(f)
            print("Loaded existing prerequisite graphs")
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            print("No existing graphs found or error loading them. Creating new graphs.")
            self.subtopic_graph = nx.DiGraph()
            self.topic_graph = nx.DiGraph()
            self.subtopic_to_topic = {}
            return False

    def save_graphs(self):
        """Save the current graphs and mapping to files"""
        # Save subtopic graph
        write_gexf(self.subtopic_graph, os.path.join(self.graphs_dir, 'subtopic_graph.gexf'))
        # Save topic graph
        write_gexf(self.topic_graph, os.path.join(self.graphs_dir, 'topic_graph.gexf'))
        # Save subtopic to topic mapping
        with open(os.path.join(self.graphs_dir, 'subtopic_to_topic.json'), 'w') as f:
            json.dump(self.subtopic_to_topic, f)

    def analyze_prerequisites(self, content: str, topics_and_subtopics: List[Tuple[str, List[str]]]) -> Dict:
        # Create agents
        content_analyst, relationship_expert, sequence_specialist = self.create_agents()

        # Task 1: Initial content and topic analysis
        task1 = Task(
            description=f"""Analyze the following content and topics to identify key concepts and their relationships:
            Content: {content}
            Topics and Subtopics:
            {topics_and_subtopics}
            
            Create a detailed analysis of how these subtopics relate to each other and what concepts are required to understand each subtopic.
            Consider the hierarchical relationship between topics and their subtopics.
            Format your response as a clear explanation of topic relationships.""",
            expected_output="A detailed analysis of the relationships between subtopics, including prerequisites and dependencies.",
            agent=content_analyst
        )

        # Task 2: Define prerequisite relationships
        task2 = Task(
            description="""Based on the content analysis, create a JSON structure defining prerequisite relationships.
            The JSON should follow this format:
            {
                "relationships": [
                    {
                        "subtopic": "Subtopic Name",
                        "parent_topic": "Parent Topic Name",
                        "prerequisites": ["Prerequisite Subtopic 1", "Prerequisite Subtopic 2"],
                        "reason": "Explanation of why these prerequisites are necessary"
                    }
                ]
            }
            Ensure all relationships are justified by the content.""",
            expected_output="A JSON structure containing prerequisite relationships between subtopics, including their parent topics and reasoning.",
            agent=relationship_expert
        )

        # Task 3: Validate and sequence topics
        task3 = Task(
            description="""Review the prerequisite relationships and create an optimal learning sequence.
            Ensure the sequence is logical and all prerequisites are met before their dependent topics.
            Validate that there are no circular dependencies.
            Return the final sequence in the same JSON format, adding a 'sequence_order' field to each topic.""",
            expected_output="A validated JSON structure with prerequisite relationships and sequence ordering, ensuring no circular dependencies.",
            agent=sequence_specialist
        )

        # Create and run the crew
        crew = Crew(
            agents=[content_analyst, relationship_expert, sequence_specialist],
            tasks=[task1, task2, task3],
            verbose=True
        )

        result = crew.kickoff()
        
        try:
            # Extract the JSON part from the result
            import re
            json_match = re.search(r'\{.*\}', result.raw, re.DOTALL)
            if json_match:
                relationships_data = json.loads(json_match.group())
                self._build_graph(relationships_data)
                # Save the updated graphs
                self.save_graphs()
                return relationships_data
            else:
                return {"error": "No valid JSON found in the result"}
        except Exception as e:
            return {"error": f"Error processing results: {str(e)}"}

    def _build_graph(self, relationships_data: Dict):
        """Build NetworkX graphs for subtopics and infer topic relationships"""
        self.subtopic_graph.clear()
        self.topic_graph.clear()
        self.subtopic_to_topic.clear()
        
        # First, build the subtopic graph and mapping
        for rel in relationships_data.get('relationships', []):
            subtopic = rel['subtopic']
            parent_topic = rel['parent_topic']
            self.subtopic_to_topic[subtopic] = parent_topic
            
            # Add subtopic nodes and edges
            self.subtopic_graph.add_node(subtopic, topic=parent_topic)
            for prereq in rel.get('prerequisites', []):
                self.subtopic_graph.add_node(prereq, topic=self.subtopic_to_topic.get(prereq, 'Unknown'))
                self.subtopic_graph.add_edge(prereq, subtopic)
        
        # Infer topic relationships from subtopic relationships
        for edge in self.subtopic_graph.edges():
            source_topic = self.subtopic_to_topic.get(edge[0])
            target_topic = self.subtopic_to_topic.get(edge[1])
            
            if source_topic and target_topic and source_topic != target_topic:
                if not self.topic_graph.has_edge(source_topic, target_topic):
                    self.topic_graph.add_edge(source_topic, target_topic)

    def visualize_graphs(self, base_output_path: str = "output/prerequisite_graph"):
        """Visualize both subtopic and topic prerequisite graphs"""
        os.makedirs(os.path.dirname(base_output_path), exist_ok=True)
        
        # Visualize subtopic graph
        plt.clf()  # Clear any existing plots
        fig, ax = plt.subplots(figsize=(15, 10))
        pos = nx.spring_layout(self.subtopic_graph, k=2, iterations=50)
        
        # Draw nodes with different colors for different parent topics
        topics = set(self.subtopic_to_topic.values())
        colors = plt.cm.rainbow(np.linspace(0, 1, len(topics)))
        topic_to_color = dict(zip(topics, colors))
        
        node_colors = [topic_to_color[self.subtopic_to_topic.get(node, 'Unknown')] 
                      for node in self.subtopic_graph.nodes()]
        
        nx.draw(self.subtopic_graph, pos, with_labels=True, 
                node_color=node_colors,
                node_size=2000, 
                font_size=8, 
                font_weight='bold',
                arrows=True, 
                edge_color='gray',
                ax=ax)
        
        # Add a legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor=color, label=topic, markersize=10)
                         for topic, color in topic_to_color.items()]
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
        
        ax.set_title("Subtopic Prerequisites Graph", pad=20)
        ax.axis('off')
        plt.savefig(f"{base_output_path}_subtopics.png", 
                    bbox_inches='tight',
                    dpi=300,
                    pad_inches=0.5)
        plt.close()
        
        # Visualize topic graph
        plt.clf()
        fig, ax = plt.subplots(figsize=(12, 8))
        pos = nx.spring_layout(self.topic_graph, k=2, iterations=50)
        
        nx.draw(self.topic_graph, pos, 
                with_labels=True, 
                node_color='lightblue',
                node_size=3000, 
                font_size=10, 
                font_weight='bold',
                arrows=True, 
                edge_color='gray',
                ax=ax)
        
        ax.set_title("Inferred Topic Prerequisites Graph", pad=20)
        ax.axis('off')
        plt.savefig(f"{base_output_path}_topics.png", 
                    bbox_inches='tight',
                    dpi=300,
                    pad_inches=0.5)
        plt.close()

    def get_learning_sequence(self) -> Dict[str, List[str]]:
        """Get optimal learning sequences for both topics and subtopics"""
        try:
            topic_sequence = list(nx.topological_sort(self.topic_graph))
            subtopic_sequence = list(nx.topological_sort(self.subtopic_graph))
            
            # Group subtopics by their parent topics while maintaining the topological order
            topic_to_subtopics = {}
            for subtopic in subtopic_sequence:
                parent_topic = self.subtopic_to_topic.get(subtopic)
                if parent_topic not in topic_to_subtopics:
                    topic_to_subtopics[parent_topic] = []
                topic_to_subtopics[parent_topic].append(subtopic)
            
            return {
                "topic_sequence": topic_sequence,
                "subtopic_sequence": subtopic_sequence,
                "topic_to_subtopics": topic_to_subtopics
            }
        except nx.NetworkXUnfeasible:
            return {
                "error": "Circular dependencies detected in the prerequisites",
                "topic_sequence": [],
                "subtopic_sequence": [],
                "topic_to_subtopics": {}
            }
