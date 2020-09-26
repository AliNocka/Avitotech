from urllib import parse
import string


ALPHABET = string.ascii_letters + string.digits

def encode(links_count):
    encoded_chars = []
    while links_count > 0:
        links_count = links_count - 1
        encoded_chars.append(links_count % len(ALPHABET))
        links_count //= len(ALPHABET)
    encoded_chars = encoded_chars[::-1]
    return ''.join([ALPHABET[sym] for sym in encoded_chars])

def is_valid_url(url):
    parsed_url = parse.urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)
