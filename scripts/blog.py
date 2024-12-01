import core


# You can tweak this if you want a custom behavior.
STEPS = [
    core.build_posts,
    core.build_css,
]

for step in STEPS:
    step()

