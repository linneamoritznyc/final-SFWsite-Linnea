"""New story images for the 9-frame version (nano-banana, carousel paintings as style reference)."""
import base64, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); TOK = os.environ['REPLICATE_API_TOKEN']
from gen import STYLE, REFS
def uri(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
PIANO = uri(f'{HERE}/raw/f3-piano-keys-k2.png')
JOBS = {
 'f3-note': ('3:4', [], 'one pinky red-brown earthworm poking its head up out of a small mound of dark soil, curiously looking up at a single large dark-brown eighth music note floating in the air above it. Only one note. Lots of white space around.'),
 'f4-stool': ('4:3', [PIANO], 'the same upright wooden piano as the first image, with the keyboard open showing white keys and black keys in correct groups of two and three, but NOTHING on top of the piano. Beside the piano stands a small wooden stool, and on the stool stand three small terracotta pots of dark soil. No worms visible, no people.'),
 'f6-triangles': ('3:4', [], 'a cut-away cross-section of the ground: the soil surface across the upper part with a few small pale green paper triangles lying on it; below the surface a vertical earthworm burrow shown in cross-section, and a pinky red-brown earthworm inside the burrow pulling one paper triangle down into the burrow by its pointed tip, so the triangle is half into the hole point first.'),
 'f7-books': ('1:1', [], 'a small neat stack of four old leather-bound books in muted browns and greens, plain spines with no lettering, slightly worn corners, one small pinky red-brown earthworm resting curled on top of the stack. White space around.'),
}
def run(name, tag):
    ar, extra, subject = JOBS[name]
    body = json.dumps({'input': {'prompt': STYLE + subject, 'image_input': extra + REFS, 'aspect_ratio': ar, 'output_format': 'png'}}).encode()
    req = urllib.request.Request('https://api.replicate.com/v1/models/google/nano-banana/predictions', body,
                                 {'Authorization': f'Bearer {TOK}', 'Content-Type': 'application/json', 'Prefer': 'wait'})
    d = json.load(urllib.request.urlopen(req, timeout=300))
    while d['status'] not in ('succeeded', 'failed', 'canceled'):
        time.sleep(3); d = json.load(urllib.request.urlopen(urllib.request.Request(d['urls']['get'], headers={'Authorization': f'Bearer {TOK}'})))
    if d['status'] != 'succeeded': print(name, tag, d.get('error')); return
    o = d['output'] if isinstance(d['output'], str) else d['output'][0]
    urllib.request.urlretrieve(o, f'{HERE}/raw/{name}-{tag}.png'); print('ok', name, tag)
if __name__ == '__main__':
    tags = sys.argv[1].split(','); names = sys.argv[2:] or list(JOBS)
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(lambda nt: run(*nt), [(n, t) for n in names for t in tags]))
