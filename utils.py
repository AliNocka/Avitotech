from urllib import parse
import string


ALPHABET = string.ascii_letters + string.digits

def encode(links_count):
	"""
	Params:
	:links_count: число, обозначающее кол-во ссылок в базе
	Returns:
	str - строка, представляющая собой закодированное число в n-ричной системе,
	где n - размерность алфавита ALPHABET

	Examples:
	Для алфавита 'abcdef' будут происходить следующие отображения:
	encode(1) --> 'a'
	encode(2) --> 'b'
	encode(7) --> 'aa'
	encode(8) --> 'ab'
	etc.
 	"""
    encoded_chars = []
    while links_count > 0:
        links_count = links_count - 1
        encoded_chars.append(links_count % len(ALPHABET))
        links_count //= len(ALPHABET)
    encoded_chars = encoded_chars[::-1]
    return ''.join([ALPHABET[sym] for sym in encoded_chars])

def is_valid_url(url):
	"""
	Проверка валидности url с использованием библиотеки urllib
	Будем считать, что если не удалось спарсить схему и домен, то по данной
	ссылке невозможно будет осуществить редирект, следовательно она не валидна

	Params:
	:url: строка с url
	Returns:
	bool - является ли переданная строка валидным url
	"""
    parsed_url = parse.urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)
