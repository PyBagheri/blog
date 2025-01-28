# Usage

### 1. Install TailwindCSS
If you want the build script to build TailwindCSS files too, you should use the standalone version. See https://tailwindcss.com/blog/standalone-cli

Change the `TAILWIND_EXECUTABLE` setting in `scripts/settings.py` to point to the executable's path, and `TAILWIND_CONFIG_FILE` to point to the tailwind config file `tailwind.config.js`.

### 2. Install the requirements
`$ pip install -r requirements.txt`

### 3. Build the blog
To build once:<br>
`$ python3 scripts/build.py`

Use the option `-w` or `--watch` to automatically rebuild on changes.

You might want to tweak some values in `scripts/settings.py`, especially the website address.

# Examples

 The example post file `examples/metadata.md` fully explains the post metadata format.

The file `info.json` stores the global website information which are supposed to change rather frequently. Its format is as follows:

```json
{
    "checkthisout": [
        "Here is some very cool thing! Check it out!",
        "https://example.com/cool/"
    ],
    "popularposts": [
        ["Post 1 title", "Post 1 url"],
        ["Post 2 title", "Post 2 url"],
    ],
    "populartags": ["tag1", "tag2", "tag3"]
}
```

