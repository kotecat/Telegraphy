import datetime
from json import dumps
from uuid import uuid4
from base64 import urlsafe_b64encode
from hashlib import sha256
from ipaddress import IPv4Address
from string import ascii_letters
from random import randint


TRANSLIT = {'ё': 'yo', 'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh',
     'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
     'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh',
     'щ': 'shh', 'ы': 'y', 'э': 'e', 'ю': 'yu', 'я': 'ya', " ": "-", "_": "_", "-": "-"}


def generate_random_str(length: str, *_, **__) -> str:
    result = ""
    length = min(2048, max(1, length))
    
    while len(result) < length:
        result += urlsafe_b64encode(
            uuid4().bytes
        ).decode().strip("=")

    return result[:length]


def generate_token(*_, **__) -> str:
    return generate_random_str(length=75)


def hex_to_b64(hex: str) -> str:
    return urlsafe_b64encode(bytes.fromhex(
        hex.replace(":", "")
    )).decode().strip("=")


def calc_sha256(*text: str, sep: str = " ", b64: bool = False) -> str:
    full_text = sep.join(text).encode()
    hex256 = sha256(full_text).hexdigest()
    return ( hex256 if not b64 else hex_to_b64(hex256) )


def json_dumps(data) -> str:
    return dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    )


def text_to_translit(text: str) -> str:
    result = []
    for char in text:
        if char in ascii_letters:
            result.append(char)
        else:
            translit = TRANSLIT.get(char.lower(), "")
            result.append(translit.title() if char.isupper() else translit)
    
    return ("".join(result)).strip("-")


def create_slug(seq: int = 1) -> str:
    curr = datetime.datetime.now(datetime.timezone.utc)
    date_text = f"{curr.month}-{curr.day}"
    date_text += "-" + str(
        ((curr.second & 0b111111) + (curr.minute << 6)) & 0b1111111111
    )
    date_text += f"-{seq}" if seq > 1 else ""
    return date_text
