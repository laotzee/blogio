import os
import shutil
import sys
import frontmatter
import asyncio
from google import genai
from google.genai.types import Schema, Type
from dotenv import load_dotenv
from src.db.helpers import save_quotes
from src.utils.helpers import check_language, get_input_files


lang, source = check_language(sys.argv)
load_dotenv()
prompt = os.getenv("PROMPT")

INPUT_FILE_PATH = os.path.join("resources/writing/", source)
USED_FILES_PATH = os.path.join("resources/writing/", source, "used")
MAX_CONCURRENT_REQUESTS = 5
MAX_POST_PER_BATCH = 15
current_model = "gemini-3.1-flash-lite-preview"

semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

response_schema = Schema(
    type=Type.ARRAY,
    description="A list of all extracted quotes.",
    items=Schema(type=Type.STRING, description="The extracted direct quote."),
)


def read_post(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            blog_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {file_path}")
        exit()

    return blog_text


async def extract_quotes(prompt, content, model, client):

    async with semaphore:
        full_prompt = (
            f"{prompt}\n\n--- BLOG POST START ---\n{content}\n--- BLOG POST END ---"
        )

        print("Calling Gemini API to extract quotes...")

        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=full_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": response_schema,
                },
            )

        except Exception as e:
            print(f"An error occurred during the API call: {e}")
            return None
        print("API call successful. Processing response...")
        return response


def process_response(response) -> list[str] | None:
    if response is None:
        return None

    try:
        return response.parsed

    except Exception as e:
        print(f"Error: Could not extract parsed data. {e}")
        return None


async def main():
    tasks = []
    data = []
    client = genai.Client()
    post_files = get_input_files(INPUT_FILE_PATH)

    for post in post_files[:MAX_POST_PER_BATCH]:
        post_path = os.path.join(INPUT_FILE_PATH, post)
        post = frontmatter.load(post_path)
        tasks.append(extract_quotes(prompt, post.content, current_model, client))
        post["path"] = post_path
        data.append(post)

    results = await asyncio.gather(*tasks)

    for result, post in zip(results, data):
        try:
            quote_list = process_response(result)
            if quote_list:
                save_quotes(quote_list, post["title"], lang)

                if os.path.exists(post["path"]):
                    shutil.move(post["path"], USED_FILES_PATH)
            else:
                print(f"Skipping {post['title']}: No quotes extracted.")
        except Exception as e:
            print(f"Failed to process {post['title']}: {e}")
            continue


if __name__ == "__main__":
    asyncio.run(main())
