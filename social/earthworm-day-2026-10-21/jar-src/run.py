import sys, subprocess, os
import slides
from lib import page
here = os.path.dirname(os.path.abspath(__file__))
for name in sys.argv[1:]:
    art, texts = getattr(slides, name)()
    open(f'{here}/{name}.html', 'w').write(page(''.join(art), texts, logo_box=(890, 1200, 150, None)))
    subprocess.run(['node', f'{here}/render.js', f'{here}/{name}.html', f'{here}/out/{name}.png'], check=True)
