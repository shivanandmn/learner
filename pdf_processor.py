import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF

class PDFProcessor:
    def __init__(self):
        load_dotenv()
        # Configure the Gemini API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def process_pdf_content(self, pdf_path):
        """Process PDF content using Gemini's vision capabilities and return raw text in markdown format"""
        # Open the PDF
        pdf_document = fitz.open(pdf_path)
        markdown_content = """"""

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            # Convert page to image for visual analysis
            pix = page.get_pixmap()
            img_path = f"temp_page_{page_num}.png"
            pix.save(img_path)
            
            try:
                # Process the page image with Gemini
                img = Image.open(img_path)
                prompt = """ Provided you a page of chapter from NCERT textbook, your task is to extract all visual text content from the image and provide it in markdown format.
                As example here below format
                # Title
                ## Sub Title
                **important point**
                image should be in this format: [[explaining about the image]]
                extract all the text from the image.
                """
                response = self.model.generate_content([prompt, img])
                markdown_content += f"""
[[PAGE NO:{page_num}]]\n\n{response.text}
"""
                
            finally:
                # Clean up temporary image file
                if os.path.exists(img_path):
                    os.remove(img_path)

        pdf_document.close()
        return markdown_content
