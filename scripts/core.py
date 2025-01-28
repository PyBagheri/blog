# TODO:
# 1. Infer build filenames from scripts/urls.py.
# 2. Building a single page rather than all.
# 3. Write tests.
# 4. General cleanup ...

import re
import json
import os
from datetime import datetime
import markdown
from rcssmin import cssmin
from jinja2 import Environment, select_autoescape, FileSystemLoader
from pygments.formatters import HtmlFormatter
import settings
import urls


jinja_env = Environment(
    loader=FileSystemLoader(settings.TEMPLATES_DIR),
    autoescape=select_autoescape()
)

jinja_env.globals.update(url=urls.url)
jinja_env.globals.update(fullurl=urls.fullurl)


POST_METADATA_REGEX = re.compile(r'^<!--METADATA$\n(.*)\n-->', re.MULTILINE | re.DOTALL)
MARKDOWN_STYLE_LINK_REGEX = re.compile(r'^\[(.*)\]\((.*)\)$')
HTML_COMMENT_REGEX = re.compile(r'<!--.*-->', re.MULTILINE | re.DOTALL)

ALLOWED_POST_METADATA_KEYS = [
    'title',
    'date',
    'lastupdated',
    'tags',
    'related',
    'thumbnail',
    'thumbnailalt',
    'hide',
    'next',
    'prev',
    
    # Used on post preview, as well as in meta tags.
    'brief',
    
    'unlisted',
]


def _postprocess_post_metadata(metadata):
    final_metadata = {}
    for key, value in metadata.items():
        # TODO: Give off a warning when this happens
        if key not in ALLOWED_POST_METADATA_KEYS:
            continue
        
        # Ignore empty values
        if not value:
            continue
            
        match key:
            case 'tags' | 'hide':
                final_metadata[key] = value.split(' ')
            case 'next' | 'prev':
                final_metadata[key] = re.findall(MARKDOWN_STYLE_LINK_REGEX, value)[0]
            case 'related':
                related_items = []
                for related in value:
                    related_items.append(re.findall(MARKDOWN_STYLE_LINK_REGEX, related)[0])
                final_metadata[key] = related_items
            case 'unlisted':
                final_metadata[key] = value.lower() in ['yes', 'true']
            case _:
                final_metadata[key] = value
    return final_metadata


def _get_pygments_styles():
    return '\n'.join([
        HtmlFormatter(
            style=settings.PYGMENTS_LIGHT_STYLE, nobackground=True
        ).get_style_defs('#main:not(.dark) .codehilite'),
        
        HtmlFormatter(
            style=settings.PYGMENTS_DARK_STYLE, nobackground=True
        ).get_style_defs('#main.dark .codehilite')
    ])


def _paginate(posts, page_size):
    number_of_pages = (len(posts) + page_size - 1) // page_size
    
    def it():
        for page in range(1, number_of_pages+1):
            post_batch = posts[page_size*(page-1):page_size*page]
            yield page, post_batch

    return number_of_pages, it()


class PageBuilder:
    def __init__(self, page_size=10):
        self.page_size = page_size
        self.posts_filenames = os.listdir(settings.POSTS_DIR)
        self.posts_filenames.sort(
            key=lambda x: datetime.strptime(x.split('.')[0], '%Y-%m-%d'),
            reverse=True
        )
        # order doesn't matter for root pages, as they are not going to
        # be listed anywhere; they must be linked directly.
        self.root_pages_filenames = os.listdir(settings.ROOT_PAGES_DIR)
        
    def _get_new_posts_data(self):
        new = []
        # We get 4 posts so that if a post is itself in the 'new',
        # we have another one as spare to include instead of that post.
        count = 0
        for post_filename in self.posts_filenames:
            _, slug, _ = post_filename.split('.')
            
            with open(settings.POSTS_DIR / post_filename) as f:
                post_metadata = self._extract_post_metadata(f.read())
            
            if post_metadata.get('unlisted', False):
                continue
            new.append((post_metadata['title'], slug))
            count += 1
            if count >= 4:
                break
        return new

    def _get_global_context(self, force_refresh=False):
        if not force_refresh and (cache := getattr(self, '_global_context', None)):
            return cache
        with open(settings.INFO_FILE) as f:
            self.site_info = json.loads(f.read())
        context = {
            'website': {
                'base_url': settings.BASE_WEBSITE_URL.value,
                'description': settings.WEBSITE_DESCRIPTION
            }
        }
        for name in ['checkthisout', 'popularposts', 'populartags']:
            if item := self.site_info.get(name, None):
                context[name] = item

        if new := self._get_new_posts_data():
            context['new'] = new
        
        self._global_context = context
        return context
    
    def _extract_post_metadata(self, content):
        result = re.findall(POST_METADATA_REGEX, content)
        if not result:
            return {}
        metadata = {}
        current_key = None
        for line in result[0].split('\n'):
            # '--' is for commented lines
            if line.lstrip().startswith('--'):
                continue
            if current_key is not None:
                if line.startswith('> '):
                    metadata[current_key].append(line[2:].strip())
                    continue
                current_key = None
            key, delim, data = line.partition(':')
            key = re.sub(r'\s+', '', key.lower())
            data = data.strip()
            if delim != ':' or not key:
                continue
            if not data:
                current_key = key
                metadata[key] = []
                continue
            metadata[key] = data
        return _postprocess_post_metadata(metadata)
    
    def _get_post_context(self, slug, content):
        context = self._extract_post_metadata(content)
        
        # For code highlighting.
        context['extra_style'] = cssmin(_get_pygments_styles())
        
        context['slug'] = slug
        
        context.update(self._get_global_context())
        
        # If the post itself is in the 'new', then don't
        # include it. Also, trim it to 3 posts max.
        if new := context.get('new', None):
            final_new = []
            for item in new:
                if item[1] == slug:
                    continue
                final_new.append(item)
            context['new'] = final_new[:3]
        
        return context
    
    def _render_post(self, content, render_context):
        template = jinja_env.get_template('blog/post.html')
    
        # Remove all comments (including metadata)
        markdown_content = re.sub(HTML_COMMENT_REGEX, '', content)
        
        html = markdown.markdown(
            markdown_content,
            extensions=['codehilite']
        )
        
        return template.render(
            content=html,
            **render_context
        )
    
    def build_all_posts(self):
        # This is to be used for building other pages.
        self.listed_posts_data = []
        
        for filename in self.posts_filenames:
            date, slug, _ = filename.split('.')
            
            # We put the 'index.html' inside a directory with the same
            # name as the post file name. The reason for this is to have
            # a trailing slash for URLs when being served on Github.
            post_dir = settings.BUILD_DIR / 'blog' / slug
            post_dir.mkdir(parents=True, exist_ok=True)
            
            with (
                open(settings.POSTS_DIR / filename) as src,
                open(post_dir / 'index.html', 'w') as dest
            ):
                content = src.read()
                post_context = self._get_post_context(slug, content)
                dest.write(self._render_post(content, post_context))
                
            if not post_context.get('unlisted', False):
                self.listed_posts_data.append({'date': date, 'context': post_context})
                

    def build_post_list_pages(self):
        if not hasattr(self, 'listed_posts_data'):
            raise ValueError('post list pages must be built after building posts')
        
        template = jinja_env.get_template('blog/postlist.html')
        
        context = self._get_global_context()
        
        (settings.BUILD_DIR / 'blog').mkdir(parents=True, exist_ok=True)
        
        number_of_pages, paginated_posts = _paginate(self.listed_posts_data, self.page_size)
        context['number_of_pages'] = number_of_pages
        
        # Build the home page even with no posts.
        if number_of_pages == 0:
            html = template.render(
                posts=[],
                **(context | {'page': 1})
            )
            with (
                # We have the home page available both at /blog/ and /.
                open(settings.BUILD_DIR / f'blog/index.html', 'w') as dest1,
                open(settings.BUILD_DIR / f'index.html', 'w') as dest2,
            ):
                dest1.write(html)
                dest2.write(html)
            return 0

        for page, post_batch in paginated_posts:
            html = template.render(
                posts=post_batch,
                **(context | {'page': page})
            )
            
            if page == 1:  # home
                with (
                    # We have the home page available both at /blog/ and /.
                    open(settings.BUILD_DIR / f'blog/index.html', 'w') as dest1,
                    open(settings.BUILD_DIR / f'index.html', 'w') as dest2,
                ):
                    dest1.write(html)
                    dest2.write(html)
                continue
            
            page_dir = settings.BUILD_DIR / 'blog' / str(page)
            page_dir.mkdir(parents=True, exist_ok=True)
            with open(page_dir / 'index.html', 'w') as dest:
                dest.write(html)
        return number_of_pages
                
    def build_tag_pages(self):
        tag_template = jinja_env.get_template('blog/tag.html')
        alltags_template = jinja_env.get_template('blog/alltags.html')
        
        tag_posts_map = {}
        for post in self.listed_posts_data:
            post_tags = post['context'].get('tags', [])
            for tag in post_tags:
                tag_posts_map[tag] = tag_posts_map.get(tag, []) + [post]
        
        context = self._get_global_context()
        
        (settings.BUILD_DIR / 'blog' / 'tags').mkdir(parents=True, exist_ok=True)
        alltags_html = alltags_template.render(
            tags_data=[(tag, len(posts)) for tag, posts in tag_posts_map.items()],
            **context
        )
        with open(settings.BUILD_DIR / f'blog/tags/index.html', 'w') as dest:
            dest.write(alltags_html)

        for tag, paginated_posts in tag_posts_map.items():
            paginated_posts.sort(
                key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
                reverse=True
            )
            
            number_of_pages, paginated_posts = _paginate(paginated_posts, self.page_size)
            context['number_of_pages'] = number_of_pages
            context['tag'] = tag
            
            for page, post_batch in paginated_posts:
                html = tag_template.render(
                    posts=post_batch,
                    **(context | {'page': page})
                )
                
                (settings.BUILD_DIR / 'blog' / 'tags' / tag).mkdir(parents=True, exist_ok=True)
                
                if page == 1:  # main page
                    with open(settings.BUILD_DIR / f'blog/tags/{tag}/index.html', 'w') as dest:
                        dest.write(html)
                    continue
                
                page_dir = settings.BUILD_DIR / 'blog' / 'tags' / tag / str(page)
                page_dir.mkdir(parents=True, exist_ok=True)
                with open(page_dir / 'index.html', 'w') as dest:
                    dest.write(html)
        return list(tag_posts_map.keys())

    def build_root_pages(self):
        for filename in self.root_pages_filenames:
            slug, _ = filename.split('.')
            
            # We put the 'index.html' inside a directory with the same
            # name as the post file name. The reason for this is to have
            # a trailing slash for URLs when being served on Github.
            page_dir = settings.BUILD_DIR / slug
            page_dir.mkdir(parents=True, exist_ok=True)
            
            with (
                open(settings.ROOT_PAGES_DIR / filename) as src,
                open(page_dir / 'index.html', 'w') as dest
            ):
                content = src.read()
                
                # For now, the root pages are also markdown files with
                # the same format as the posts; so post-specific methods
                # will also work on them. This might change later.
                page_context = self._get_post_context(slug, content)
                dest.write(self._render_post(content, page_context))
