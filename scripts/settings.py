from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


########## settings begin from here ##########

TEMPLATES_DIR = BASE_DIR / 'templates'

POSTS_DIR = BASE_DIR / 'posts'

TAILWIND_EXECUTABLE = BASE_DIR / 'tailwindcss'

BUILD_DIR = BASE_DIR / 'build'
