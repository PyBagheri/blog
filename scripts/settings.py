from pathlib import Path
from utils import URL


BASE_DIR = Path(__file__).parent.parent


########## settings begin from here ##########

TEMPLATES_DIR = BASE_DIR / 'templates'

PYGMENTS_LIGHT_STYLE = 'default'
PYGMENTS_DARK_STYLE = 'lightbulb'

POSTS_DIR = BASE_DIR / 'posts'
ROOT_PAGES_DIR = BASE_DIR / 'pages'

TAILWIND_EXECUTABLE = BASE_DIR / 'tailwindcss'
TAILWIND_CONFIG_FILE = BASE_DIR / 'tailwind.config.js'

STATICS_DIR = BASE_DIR / 'static'

# Github only recognizes the root and /docs directory as
# custom paths. Since we have other stuff in our root which
# we don't want in the blog, /docs is our only option.
BUILD_DIR = BASE_DIR / 'docs'

INFO_FILE = BASE_DIR / 'info.json'

BASE_WEBSITE_URL = URL('https://bagheri.io/')

CNAME = 'bagheri.io'

WEBSITE_DESCRIPTION = 'Here I share my thoughts and what I learn.'
