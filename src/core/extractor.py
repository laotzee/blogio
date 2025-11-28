import os, json, shutil, sys
from google import genai
from google.genai.types import Schema, Type
from dotenv import load_dotenv
from src.db.helpers import save_quotes
from src.utils.helpers import check_language, get_input_files
    
lang, source = check_language(sys.argv)
load_dotenv()
prompt = os.getenv('PROMPT') 

INPUT_FILE_PATH = os.path.join('resources/writing/', source)
USED_FILES_PATH = os.path.join('resources/writing/', source, 'used')  

current_model="gemini-2.5-pro"
new_model="gemini-3-pro-preview"

response_schema = Schema(
    type=Type.ARRAY,
    description="A list of all extracted quotes.",
    items=Schema(type=Type.STRING, description="The extracted direct quote.")
)

def read_post(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            blog_text = f.read() 
    except FileNotFoundError:
        print(f"Error: Input file not found at {file_path}")
        exit()

    return blog_text

def extract_quotes(prompt, content, model):

    client = genai.Client()

    full_prompt = (
        f"{prompt}\n\n"
        "--- BLOG POST START ---\n"
        f"{content}\n" 
        "--- BLOG POST END ---"
    )

    print("Calling Gemini API to extract quotes...")

    try:
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema,      
            },
        )

    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        exit()
    print("API call successful. Processing response...")
    return response

def process_json(response) -> list[str]:
    try:
        quotes_list = json.loads(response.text)
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from the API.")
        print("Raw API Response Text:", response.text)
        exit()

    return quotes_list


if __name__ == '__main__':
    post_files = get_input_files(INPUT_FILE_PATH)
    for post in post_files:
        post_path = os.path.join(INPUT_FILE_PATH, post)
        content = read_post(post_path)
        response = extract_quotes(prompt, content, new_model)
        quote_list = process_json(response)
        save_quotes(quote_list, post, lang)
        shutil.move(post_path, USED_FILES_PATH)
