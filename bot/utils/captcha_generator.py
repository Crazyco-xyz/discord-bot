import random
import string
import typing
from io import BytesIO

from PIL import ImageFilter, ImageDraw, Image
from captcha.image import ImageCaptcha, ColorTuple, Draw
from captcha.audio import AudioCaptcha


CAPTCHA_CODE_LENGTH = 6


def add_lines(image):
    width = random.randrange(6, 8)
    co1 = random.randrange(0, 75)
    co3 = random.randrange(275, 350)
    co2 = random.randrange(40, 65)
    co4 = random.randrange(40, 65)
    draw = ImageDraw.Draw(image)
    draw.line([(co1, co2), (co3, co4)], width=width, fill=(90, 90, 90))


def add_noise(image):
    noise_percentage = 0.25  # 25%

    pixels = image.load()  # create the pixel map
    for i in range(image.size[0]):  # for every pixel:
        for j in range(image.size[1]):
            rdn = random.random()  # Give a random %
            if rdn < noise_percentage:
                pixels[i, j] = (90, 90, 90)


def create_noise_curve(image: Image, color: ColorTuple) -> Image:
    w, h = image.size
    x1 = random.randint(0, int(w / 10))
    x2 = random.randint(w - int(w / 10), w)
    y1 = random.randint(int(h / 10), h - int(h / 10))
    y2 = random.randint(y1, h - int(h / 10))
    points = [x1, y1, x2, y2]
    end = random.randint(160, 200)
    start = random.randint(0, 20)
    Draw(image).arc(points, start, end, fill=color, width=2)
    return image


def gen_code(length: int = CAPTCHA_CODE_LENGTH, use_letters=True):
    return "".join(random.choice((string.ascii_uppercase if use_letters else "") + string.digits) for _ in range(length))


def generate_audio(path) -> str:
    audio_captcha = AudioCaptcha()
    code = gen_code(use_letters=False)
    audio_captcha.write(code, path)
    return code


def generate_captcha(font_path, background_color: tuple[int, int, int], text_color: tuple[int, int, int]) -> typing.Tuple[str, BytesIO]:
    image_captcha = ImageCaptcha(width=280, height=90, fonts=[font_path])

    captcha_string = gen_code()

    image: Image = image_captcha.create_captcha_image(chars=captcha_string, color=text_color,
                                                      background=background_color)  # old value: (88, 101, 242)

    image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    image.filter(ImageFilter.CONTOUR)
    image.filter(ImageFilter.EDGE_ENHANCE_MORE)

    image_captcha.create_noise_dots(image, (35, 39, 42), number=60)

    add_lines(image)
    add_noise(image)

    out = BytesIO()
    image.save(out, format="png")
    out.seek(0)

    return captcha_string, out
