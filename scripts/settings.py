from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


########## settings begin from here ##########

TEMPLATES_DIR = BASE_DIR / 'templates'

POSTS_DIR = BASE_DIR / 'posts'

TAILWIND_EXECUTABLE = BASE_DIR / 'tailwindcss'

STATICS_DIR = BASE_DIR / 'static'

# Github only recognizes the root and /docs directory as
# custom paths. Since we have other stuff in our root which
# we don't want in the blog, /docs is our only option.
BUILD_DIR = BASE_DIR / 'docs'
