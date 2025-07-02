import google.generativeai as genai

# Configure the Gemini API with your key
genai.configure(api_key="YOUR API")

# Create a Gemini model instance
model = genai.GenerativeModel('gemini-pro')

def enhance_text(text: str) -> str:
    """Enhances the given text using the Gemini API."""
    prompt = f"Please correct and improve the following OCR'd text. Fix any spelling or grammatical errors, and format it for better readability:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text
