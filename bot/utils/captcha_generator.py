from io import BytesIO

from captcha.image import ImageCaptcha, Image, ColorTuple, Draw
from PIL import ImageFilter
import string
import random
import typing


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


def generate_captcha() -> typing.Tuple[str, BytesIO]:
    image = ImageCaptcha(width=280, height=90)

    available_strings = [string.digits, string.ascii_letters]

    captcha_string = ""
    for i in range(5):
        captcha_string += random.choice(random.choice(available_strings))

    data = image.create_captcha_image(chars=captcha_string, color=(82, 94, 236), background=(88, 101, 242))

    data.filter(ImageFilter.EDGE_ENHANCE_MORE)
    data.filter(ImageFilter.CONTOUR)
    data.filter(ImageFilter.EDGE_ENHANCE_MORE)

    image.create_noise_dots(data, (35, 39, 42), number=60)

    create_noise_curve(data, (35, 39, 42))

    out = BytesIO()
    data.save(out, format="png")
    out.seek(0)

    return captcha_string, out
