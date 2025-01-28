import subprocess
import os
import shutil

from printing import title, error, warning, bulletlist, info, endsection
import settings
import core


def cleanup_build_directory(remove_static=False):
    if not settings.BUILD_DIR.exists():
        return
    
    title('Cleaning up the old build directory')
    
    # https://stackoverflow.com/questions/185936
    # It's important that we don't remove the build directory itself,
    # as it can be used as a serving point, and the server program would
    # crash after every build.
    for filename in os.listdir(settings.BUILD_DIR):
        # When we remove the statics, some tools like TailwindCSS
        # stop working properly. So, we keep it when we have the
        # watch option enabled.
        if filename == 'static' and not remove_static:
            continue
        
        file_path = os.path.join(settings.BUILD_DIR, filename)
        
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    endsection()


def build_css(watch=False):
    (settings.BUILD_DIR / 'static').mkdir(parents=True, exist_ok=True)
    
    arg_list = [
        settings.TAILWIND_EXECUTABLE,
        '-i',
        settings.STATICS_DIR / 'css/main.css',
        '-o',
        settings.BUILD_DIR / 'static/main.css',
        '-c',
        settings.TAILWIND_CONFIG_FILE,
        '--minify',
    ]
    
    if watch:
        arg_list.append('-w')
    
    if settings.TAILWIND_EXECUTABLE.exists():
        title('starting TailwindCSS watcher' if watch else 'building TailwindCSS files')
        process = subprocess.Popen(arg_list)
        if watch:
            return process
        process.wait()
        endsection()
        return
    
    warning([
        f'WARNING: no tailwind executable at {settings.TAILWIND_EXECUTABLE}.',
        'Skipping CSS build.',
    ])


def collect_static_directory(dirname, *, plural_name=None, log_count=False):
    plural_name = plural_name or dirname
    
    title(f'collecting {plural_name}')
    
    build_dir = settings.BUILD_DIR / 'static' / dirname
    source_dir = settings.STATICS_DIR / dirname
    
    if not source_dir.exists():
        warning(f"No static directory '{dirname}'. Skipping.")
        return
    
    build_dir.mkdir(parents=True, exist_ok=True)
    
    if log_count:
        info(f'{len(os.listdir(source_dir))} {plural_name} found')
    
    build_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, build_dir, dirs_exist_ok=True)
    
    endsection()


def collect_images():
    collect_static_directory('images', log_count=True)


def collect_thumbnails():
    collect_static_directory('thumbnails', log_count=True)


def collect_other_statics():
    collect_static_directory('icons', log_count=True)
    collect_static_directory('fonts')


def build_all_pages():
    title('building posts')
    builder = core.PageBuilder()
    if builder.posts_filenames:
        bulletlist('Posts found:', builder.posts_filenames)
    else:
        warning('No posts found.')
    endsection()
    builder.build_all_posts()
    
    title('building post pages')
    number_of_pages = builder.build_post_list_pages()
    if number_of_pages == 0:
        warning(f'No posts found. Only built the home page.')
    else:
        info(f'Built {number_of_pages} post pages.')
    endsection()
    
    title('building tag pages')
    tags = builder.build_tag_pages()
    if tags:
        bulletlist(f'Tags found:', tags)
    else:
        warning(f'No tags found.')
    endsection()
    
    title('building root pages')
    if builder.root_pages_filenames:
        bulletlist('Root pages found:', builder.root_pages_filenames)
    else:
        warning('No root pages found.')
    builder.build_root_pages()
    endsection()


def create_cname():
    title('creating the CNAME file')
    
    settings.BUILD_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(settings.BUILD_DIR / 'CNAME', 'w') as f:
        f.write(settings.CNAME)
    
    endsection()
