from pdf_processor import PDFProcessor
from topic_extractor import TopicExtractor
from question_generator_crew import QuestionGeneratorCrew
from prerequisite_analyzer import PrerequisiteAnalyzer
from data_manager import DataManager
import os

def save_markdown(content, file_path):
    """Utility function to save content to a markdown file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as md_file:
        md_file.write(content)

def read_markdown(file_path):
    """Utility function to read content from a markdown file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    
    with open(file_path, "r", encoding="utf-8") as md_file:
        return md_file.read()

def main():
    # Initialize the processors
    pdf_processor = PDFProcessor()
    topic_extractor = TopicExtractor()
    question_generator = QuestionGeneratorCrew()
    prerequisite_analyzer = PrerequisiteAnalyzer()
    data_manager = DataManager()
    
    # Path to your 5th grade geography PDF
    pdf_path = "data/eeap101.pdf"
    
    # Process the PDF
    # print("Processing PDF...")
    # processed_content = pdf_processor.process_pdf_content(pdf_path)

    # Save the extracted content as a markdown file
    output_path = f"output/{pdf_path.split('/')[-1].split('.')[0]}.md"
    # save_markdown(processed_content, output_path)
    
    # print(f"Extracted content saved to {output_path}")

    # Read and print the saved markdown content (for verification)
    print("Reading saved markdown file...")
    processed_content = read_markdown(output_path)

    # Extract topics and subtopics
    print("\nExtracting topics and subtopics...")
    topics_and_subtopics = topic_extractor.extract_topics_and_subtopics(processed_content)
    
    # Check if we need to analyze prerequisites
    if not os.path.exists(os.path.join("output/graphs", "subtopic_graph.gexf")):
        print("\nAnalyzing subtopic prerequisites...")
        prerequisite_data = prerequisite_analyzer.analyze_prerequisites(processed_content, topics_and_subtopics)
    else:
        print("\nUsing existing prerequisite graphs...")
        prerequisite_data = {
            "relationships": [
                {
                    "subtopic": subtopic,
                    "parent_topic": prerequisite_analyzer.subtopic_to_topic[subtopic],
                    "prerequisites": list(prerequisite_analyzer.subtopic_graph.predecessors(subtopic))
                } for subtopic in prerequisite_analyzer.subtopic_graph.nodes()
            ]
        }
    
    # Generate prerequisite graphs visualization
    prerequisite_analyzer.visualize_graphs("output/prerequisite_graph")
    
    # Get optimal learning sequences
    sequences = prerequisite_analyzer.get_learning_sequence()
    
    if "error" in sequences:
        print(f"\nError in sequencing: {sequences['error']}")
    else:
        # Print topic sequence
        print("\nOptimal Topic Learning Sequence:")
        for i, topic in enumerate(sequences['topic_sequence'], 1):
            print(f"{i}. {topic}")
            # Print subtopics for this topic
            subtopics = sequences['topic_to_subtopics'].get(topic, [])
            for j, subtopic in enumerate(subtopics, 1):
                print(f"   {i}.{j} {subtopic}")
        # Process topics and subtopics in the optimal sequence
        for topic in sequences['topic_sequence']:
            print(f"\nProcessing topic: {topic}")
            
            # Get subtopics for this topic in their optimal order
            subtopics = sequences['topic_to_subtopics'].get(topic, [])
            
            # Add topic and subtopics to data manager
            data_manager.add_topic(topic, subtopics)
            
            # Generate questions for this topic using CrewAI
            questions = question_generator.generate_questions(processed_content, topic, subtopics)
            data_manager.add_questions(topic, questions)
            
    # Save prerequisite data
    data_manager.add_prerequisites(prerequisite_data)
    
    # Select random topics and prepare final structure
    # data_manager.prepare_selected_topics()
    
    # Save everything to JSON
    data_manager.save_to_json()
    print("\nAll content has been processed and saved to output/content.json")

if __name__ == "__main__":
    main()
