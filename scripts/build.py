import commands
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import threading
import settings
from printing import warning, endsection


STEPS_WITHOUT_CSS_BUILD = [
    commands.cleanup_build_directory,
    commands.collect_images,
    commands.collect_thumbnails,
    commands.collect_other_statics,
    commands.build_all_pages,
    commands.create_cname,
]

def run_all_except_css_build():
    for step in STEPS_WITHOUT_CSS_BUILD:
        step()


lock = threading.Lock()
class FileModifiedHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not lock.acquire(blocking=False):
            return
        try:
            warning('Rebuilding ...\n')
            run_all_except_css_build()
            endsection()
        # Upon editing the files, there might be certain errors which only
        # happen because the editing has not finished yet. We don't want the
        # entire script to crash, so we catch the exceptions.
        #
        # TODO: Make the exceptions more specific.
        except Exception:
            pass
        finally:
            lock.release()
    
    
def start_rebuild_observer(path):
    event_handler = FileModifiedHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True, event_filter=[FileModifiedEvent])
    observer.start()
    return observer


if __name__ == '__main__':
    watch = len(sys.argv) > 1 and sys.argv[1].lower() in ['-w', '--watch']
    
    if not watch:
        run_all_except_css_build()
        commands.build_css(watch=False)
        exit()
    
    run_all_except_css_build()
    templates_observer = start_rebuild_observer(settings.TEMPLATES_DIR)
    posts_observer = start_rebuild_observer(settings.POSTS_DIR)
    root_pages_observer = start_rebuild_observer(settings.ROOT_PAGES_DIR)
    info_file_observer = start_rebuild_observer(settings.INFO_FILE)
    commands.build_css(watch=True)  # starts the tailwind observer
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        templates_observer.stop()
        posts_observer.stop()
        root_pages_observer.stop()
        info_file_observer.stop()
        
        templates_observer.join()
        posts_observer.join()
        root_pages_observer.join()
        info_file_observer.join()
