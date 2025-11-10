import logging, os, sys, random, shutil
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from dotenv import load_dotenv
from src.utils.helpers import check_language, get_input_files
from src.db.helpers import unpublished_quote, update_published_quote


def login_user(settings:bool = False) -> Client:
    """
    Attempts to login to Instagram using either the provided session
    information or the provided username and password.
    """
    login_failed = False
    cl = Client()
    if settings:
        print('settings found')
        cl.load_settings("session.json")
        cl.login(USERNAME, PASSWORD)
        try:
            cl.get_timeline_feed()
        except LoginRequired:
            login_failed = True

    if not settings or login_failed:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings("session.json")

    return cl

def caption_generator(quote: str, post_title: str, lang) -> str:
    
    if lang == 1:
        caption = f"Fragment from '{post_title}'.\n{quote}"
    elif lang == 2:
        caption = f"Fragmento de '{post_title}'.\n'{quote}'"
    else:
        caption = ''
    return caption

if __name__ == '__main__':

    load_dotenv()
    USERNAME = os.getenv('IG_USER')
    PASSWORD = os.getenv('IG_PASSWORD')
    SESSION = 'session.json'

    lang, source = check_language(sys.argv)
    base_path = os.path.join('resources/posts', source)
    used_path = os.path.join('resources/posts', source, 'used')
    base_files = get_input_files('.')
    session_set = SESSION in base_files
    lang, source = check_language(sys.argv)

    quote = unpublished_quote(lang)
    if quote == None:
        print(f"No more quotes on folder {source}. Aborting process")
        exit()

    quote_path = os.path.join(base_path, quote.img_path)
    caption =  caption_generator(quote.text, quote.title, lang)

    cl = login_user(SESSION)

    media = cl.photo_upload(
        quote_path,
        caption,
        extra_data={
        }
    )

    update_published_quote(quote.id)
    shutil.move(quote_path, used_path)
