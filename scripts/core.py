from printing import title, error, warning, bulletlist
from jinja2 import Environment, select_autoescape, FileSystemLoader
import markdown
import subprocess
import settings
import utils
import os


jinja_env = Environment(
    loader=FileSystemLoader(settings.TEMPLATES_DIR),
    autoescape=select_autoescape()
)


def build_posts():
    title('building posts')
    
    template = jinja_env.get_template('blog/post.html')
    
    posts = os.listdir(settings.POSTS_DIR)
    bulletlist('Posts found:', posts)
    
    for post in posts:
        with (
            open(settings.POSTS_DIR / post) as src,
            open(settings.BUILD_DIR / f'blog/{utils.change_extention(post, 'html')}', 'w') as dest
        ):
            dest.write(
                template.render(
                    content=markdown.markdown(src.read())
                )
            )



def build_css():
    if settings.TAILWIND_EXECUTABLE.exists():
        title('building TailwindCSS files')
        subprocess.run([
            settings.TAILWIND_EXECUTABLE,
            '-i',
            'static/css/main.css',
            '-o',
            'build/static/main.css',
            '--minify'
        ])
        return
    
    warning([
        f'WARNING: no tailwind executable at {settings.TAILWIND_EXECUTABLE}.',
        'Skipping CSS build.',
    ])

