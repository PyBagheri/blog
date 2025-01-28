import urllib


def change_extention(filename, new_extension):
    return '.'.join(filename.split('.')[:-1] + [new_extension])


def remove_extention(filename):
    return '.'.join(filename.split('.')[:-1])


class URL:
    def __init__(self, value):
        if not value.endswith('/'):
            value = value + '/'
        self.value = value
    
    def __truediv__(self, url):
        if isinstance(url, str):
            if not url.endswith('/'):
                url = url + '/'
            return URL(urllib.parse.urljoin(self.value, url))
        elif isinstance(url, URL):
            return URL(urllib.parse.urljoin(self.value, url.value))
        raise ValueError("'url' must be either a string or a URL object")
    
    def __repr__(self):
        return f'<URL: {self.value}>'
