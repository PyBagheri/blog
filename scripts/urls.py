from settings import BASE_WEBSITE_URL


def get_post_page(page):
    if page == 1:
        return '/'
    return f'/blog/{page}/'

def get_tag_page(tag, page):
    if page == 1:
        return f'/blog/tags/{tag}/'
    return f'/blog/tags/{tag}/{page}/'
    

urlpatterns = {
    'home': '/',
    'postpage': get_post_page,
    'tagpage': get_tag_page,
    'alltags': '/blog/tags/',
    'tag': '/blog/tags/{tag}/',
    'post': '/blog/{slug}/',
    'about': '/about/',
    
    # static
    'static': '/static/{path}',
    'thumbnail': '/static/thumbnails/{filename}',
}


def url(name, **kwargs):
    value = urlpatterns[name]  # error if doesn't exist
    if callable(value):
        return value(**kwargs)
    elif isinstance(value, str):
        return value.format(**kwargs)


def fullurl(name, **kwargs):
    final = (BASE_WEBSITE_URL / url(name, **kwargs)).value
    
    # For file names, we don't want slashes.
    if name in ('static', 'thumbnail'):
        return final.rstrip('/')
    return final
