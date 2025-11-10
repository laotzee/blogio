import os

def check_language(lang: list) -> tuple:
    valid_lang = ('en', 'es')
    if len(lang) == 1:
        print("No arguments given")
        exit()
    elif lang[1] not in valid_lang:
        print(f'Invalid argument given. It must be some of {valid_lang}')
        print(lang)
        exit()
    lang = (1, valid_lang[0]) if lang[1] == 'en' else (2, 'es')
    return lang


def get_input_files(input_path: str) -> list[str]:
    """Returns a list of files contained in the input_file"""
    all_items = os.listdir(input_path)
    files_only = [
        item for item in all_items 
        if os.path.isfile(os.path.join(input_path, item))
    ]
    return files_only

