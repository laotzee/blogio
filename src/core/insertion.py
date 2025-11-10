import sys, os, csv, shutil
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont
from random import choices

from src.core.background import (BACKGROUND_COLOR, TEXT_COLOR,
                                 get_text_dimensions)
from src.db.helpers import (unrendered_quotes, update_rendered_quote,
                            SessionLocal)
from src.utils.helpers import get_input_files, check_language


lang, source = check_language(sys.argv)

INPUT_FILE_PATH = 'resources/factory_background'
OUTPUT_FILE_PATH = os.path.join('resources/posts/', source)

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1440

FONT_SIZE = 64
FONT_PATH = 'resources/fonts/roboto/static/Roboto-Regular.ttf'
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

BOX_HORIZONTAL_MARGIN = 20 
BOX_VERTICAL_PADDING = 20
BOX_INTERNAL_TEXT_PADDING = 20 

def unique_filename() -> str:
    """Returns a UUID in string format as filename"""
    filename = str(uuid4())
    return  filename + '.jpeg'


def get_wrapped_text(text: str, 
                     font: ImageFont.FreeTypeFont,
                     max_width: int
                     ) -> str:
    """
    Wraps text to fit a specified pixel width.
    """
    lines = []
    
    if not text:
        return ""

    words = text.split()
    
    if not words:
        return ""

    current_line = words[0]
    for word in words[1:]:
        test_line = f"{current_line} {word}"
        
        if font.getlength(test_line) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    lines.append(current_line)
    
    return "\n".join(lines)


def create_quote(quote: str) -> Image:
    """Returns and image with a quote"""

    box_width = CANVAS_WIDTH - (2 * BOX_HORIZONTAL_MARGIN)
    text_max_width = box_width - (2 * BOX_INTERNAL_TEXT_PADDING)
    wrapped_text = get_wrapped_text(quote, font, text_max_width)

    image = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT))
    draw = ImageDraw.Draw(image)

    text_width, text_height = get_text_dimensions(
        draw, 
        wrapped_text, 
        font=font, 
        align='center'
    )

    BOX_HEIGHT = text_height + (2 * BOX_VERTICAL_PADDING)

    BOX_X0 = BOX_HORIZONTAL_MARGIN
    BOX_X1 = CANVAS_WIDTH - BOX_HORIZONTAL_MARGIN

    BOX_Y0 = (CANVAS_HEIGHT - BOX_HEIGHT) / 2
    BOX_Y1 = (CANVAS_HEIGHT + BOX_HEIGHT) / 2

    draw.rectangle([BOX_X0, BOX_Y0, BOX_X1, BOX_Y1], fill=BACKGROUND_COLOR)

    CANVAS_CENTER_X = CANVAS_WIDTH / 2
    CANVAS_CENTER_Y = CANVAS_HEIGHT / 2

    draw.multiline_text(
        (CANVAS_CENTER_X, CANVAS_CENTER_Y),
        wrapped_text,
        fill=TEXT_COLOR,
        font=font,
        anchor='mm',
        align='right'
    )
    return image


if __name__ == '__main__':

    backgrounds = get_input_files(INPUT_FILE_PATH)
    db = SessionLocal()
    quotes = unrendered_quotes(lang, db)   
    random_background = choices(backgrounds, k=len(quotes))

    for background, quote in zip(random_background, quotes):
        overlay = create_quote(quote.text)
        img_path = os.path.join(INPUT_FILE_PATH, background)
        base_img = Image.open(img_path).convert('RGBA')
        final_image = Image.alpha_composite(base_img, overlay)
        final_image = final_image.convert("RGB")
        filename = unique_filename()
        file_path = os.path.join(OUTPUT_FILE_PATH, filename)
        final_image.save(file_path, format='JPEG')
        update_rendered_quote(quote, filename, db)
    db.commit()
