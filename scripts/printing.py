import enum


class Colors(enum.IntEnum):
    GREEN = 32
    BLUE = 34
    RED = 31
    YELLOW = 33


def bulletize(text, bullet='>'):
    if isinstance(text, str):
        text = [text]
    return '\n'.join([f'{bullet} {t}' for t in text])


def color(text, color):
    return f'\u001b[{color.value}m{text}\u001b[0m'


def title(text):
    print(color(f'{bulletize(text)}\n', Colors.GREEN))


def error(text):
    print(color(f'{bulletize(text)}\n', Colors.RED))


def warning(text):
    print(color(f'{bulletize(text)}\n', Colors.YELLOW))


def bulletlist(title, text_list):
    print(title)
    for text in text_list:
        print('  ' + bulletize(text, '●'))
    print()
    