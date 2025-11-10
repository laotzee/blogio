import os
import shutil
from PIL import Image, ImageDraw, ImageFont
from src.utils.helpers import get_input_files

TITLE = "Dialogues"

INPUT_FILE_PATH = 'resources/background'
USED_FILES_PATH = 'resources/background/used'
OUTPUT_FILE_PATH = 'resources/factory_background/'
FONT_PATH =  "resources/fonts/DMSerif/DMSerifText-Regular.ttf"
TITLE_SIZE = 64
FONT = ImageFont.truetype(FONT_PATH, TITLE_SIZE)

IMG_SIZE = (1080, 1440)
BACKGROUND_COLOR = (0, 0, 0, 180) 
TEXT_COLOR = (255, 255, 255)
IMG_PROPORTION = (3,4)

X, Y = 20, 1200
PADDING = 30

def proportion_cal(prop: tuple[int,int],
                   width: int,
                   height: int) -> list[int, int]:
    """Returns a list containing the width and height adjusted to the 
    given proportion"""
    new_width = (height * prop[0])//prop[1]
    if new_width > width:
        height = (width * prop[1])//prop[0]
    else:
        width = new_width
    return [width, height]


def center_adjustment(width: int, scaled_width: int) -> tuple[int, int]:
    """Returns the size of the margin and the center-aligned scaled_width"""
    margin = 0
    if width - scaled_width > 0:
        margin = (width - scaled_width)//2
    scaled_width += margin
    return margin, scaled_width


def get_text_dimensions(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    **kwargs
    ) -> tuple[int, int]:
    """Calculates the pixel width and height of a text block"""
    if "\n" in text:
        bbox = draw.multiline_textbbox((0, 0), text, font=font, **kwargs)
    else:
        bbox = draw.textbbox((0, 0), text, font=font, **kwargs)
    
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def create_overlay(w: int, h:int) -> Image:
    """Creates an empty image of size w x h"""
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return overlay


def box_position(w: int, h: int, padding: int) -> tuple[int, int, int, int]:
    """Returns coordinates for the given box"""

    coords = (
        -padding,
        Y ,
        X + w + padding,
        Y + h + padding,
    )
    return coords


def create_logo(text: str) -> Image:
    """Places logo on an overlay"""
    overlay = create_overlay(IMG_SIZE[0], IMG_SIZE[1])
    blog_title = ImageDraw.Draw(overlay)

    text_w, text_h = get_text_dimensions(blog_title, text, font=FONT)

    blog_title.rounded_rectangle(
        box_position(text_w, text_h, PADDING),
        fill=BACKGROUND_COLOR,
        radius=20
    )

    blog_title.text(
        (X, Y),
        text,
        fill=TEXT_COLOR,
        font=FONT,
    )
    
    return overlay


def standardize_size(img_path: str, proportion: tuple[int,int]) -> Image:
    """
    Returns a RGBA subrectangle image from img_path that matches 
    IMG_PROPORTION and IMG_SIZE
    """
    original_img = Image.open(img_path)
    resolution = proportion_cal(
        proportion,
        original_img.width,
        original_img.height
    )
    margin_left, resolution[0] = center_adjustment(
        original_img.width,
        resolution[0]
    )
    margin_top, resolution[1] = center_adjustment(
        original_img.height,
        resolution[1]
    )
    standard_img = original_img.crop(
        (margin_left, margin_top, resolution[0], resolution[1])
    )
    standard_img = standard_img.resize(IMG_SIZE).convert('RGBA')
    return standard_img


def standardize_background(file_name: str,
                           title: str,
                           proportion: tuple[int, int]
                           ) -> None:
    """
    Saves to OUTPUT_FILE_PATH a new image that complies with IMG_SIZE and
    IMG_PROPORTION, along with an overlay ontop
    """
    img_path = os.path.join(INPUT_FILE_PATH, file_name)
    img = standardize_size(img_path, IMG_SIZE)
    w, h = img.size

    overlay = create_logo(title)

    final_image = Image.alpha_composite(img, overlay)
    final_image = final_image.convert("RGB")
    final_image.save(os.path.join(OUTPUT_FILE_PATH, file_name), format="JPEG")
    try:
        shutil.move(img_path, USED_FILES_PATH)
        
    except shutil.Error as e:
        print(f"An unexpected shutil error occurred: {e}")
            

if __name__ == '__main__':
    files_only = get_input_files(INPUT_FILE_PATH)
    for file in files_only:
        standardize_background(file, TITLE, IMG_SIZE)
