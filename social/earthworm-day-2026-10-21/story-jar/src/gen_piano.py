"""Remake the frame 3 piano with the keyboard open, editing the earlier painting (nano-banana)."""
import base64, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); TOK = os.environ['REPLICATE_API_TOKEN']
def uri(p, mime): return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()
PROMPT = ('Edit the first image. Keep the same loose watercolor science-book style, the same upright wooden piano, the same three '
          'terracotta pots of soil on top, the same pinky red-brown worm and the same small paper triangles on the piano lid, '
          'the same plain white background. Change only the keyboard: the key cover is open and a full keyboard is clearly visible '
          'across the front of the piano, white keys with black keys in the correct repeating groups of two and three, drawn with thin '
          'dark ink outlines. No text, no letters, no people, no hands.')
def run(tag):
    body = json.dumps({'input': {'prompt': PROMPT, 'image_input': [uri(f'{HERE}/raw/f3-piano-t1.png', 'image/png'), uri(f'{HERE}/ref-jar.jpg', 'image/jpeg')],
                                 'aspect_ratio': '4:3', 'output_format': 'png'}}).encode()
    req = urllib.request.Request('https://api.replicate.com/v1/models/google/nano-banana/predictions', body,
                                 {'Authorization': f'Bearer {TOK}', 'Content-Type': 'application/json', 'Prefer': 'wait'})
    d = json.load(urllib.request.urlopen(req, timeout=300))
    while d['status'] not in ('succeeded', 'failed', 'canceled'):
        time.sleep(3); d = json.load(urllib.request.urlopen(urllib.request.Request(d['urls']['get'], headers={'Authorization': f'Bearer {TOK}'})))
    if d['status'] != 'succeeded': print(tag, d.get('error')); return
    o = d['output'] if isinstance(d['output'], str) else d['output'][0]
    urllib.request.urlretrieve(o, f'{HERE}/raw/f3-piano-keys-{tag}.png'); print('ok', tag)
with ThreadPoolExecutor(2) as ex: list(ex.map(run, sys.argv[1:]))
