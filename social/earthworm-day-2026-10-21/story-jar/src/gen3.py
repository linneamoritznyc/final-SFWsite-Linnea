"""Images for the 10-frame story (nano-banana, carousel paintings as style reference)."""
import base64, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); TOK = os.environ['REPLICATE_API_TOKEN']
from gen import STYLE, REFS
def uri(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
STYLE = STYLE.replace('no people, no hands', 'no people (a hand is allowed only where asked)')
FULL = ' The whole subject is fully inside the picture with its bottom edge drawn, nothing cropped, nothing fading out, white space all around.'
JOBS = {
 'g1-jar': ('3:4', [uri(f'{HERE}/raw/f1-jar-t3.png')], 'Edit the first image: keep the jar, its soil layers, leaves and the worm in the green striped party hat exactly the same, but zoom out so the entire jar is visible, including its rounded glass bottom with a layer of pebbles at the bottom.'),
 'g3-calm': ('3:4', [], 'a small pile of dark soil in the centre. A single dark-brown music note floats in the air at the upper LEFT. One pinky red-brown earthworm pokes up out of the soil and bends its head towards the RIGHT, away from the note, so the back of its head faces the note; its eyes are calmly closed in a peaceful, unbothered expression.'),
 'g4-piano': ('4:3', [uri(f'{HERE}/raw/f3-piano-keys-k2.png')], 'an upright wooden piano like the first image, keyboard open with white keys and black keys in correct groups of two and three clearly visible. On top of the piano stands ONE terracotta clay pot of dark soil. The pot is drawn cut-away (like a cross-section) so the soil inside is visible: small wavy vibration lines run from the piano top up into the soil, and a pinky red-brown earthworm inside the soil is diving head first DOWNWARDS, its head pointing to the bottom of the pot, with just the tip of its tail at the soil surface. No steam, no other pots, no paper triangles.'),
 'g5-web': ('1:1', [], 'a simple soil food web diagram: a fallen brown leaf, a cluster of tiny rod-shaped bacteria, white branching fungal threads, a round amoeba-like protozoan, a thin clear nematode, and a pinky red-brown earthworm, arranged in a loose circle and connected to each other by thin hand-drawn brown arrows. No labels.'),
 'g6-bite': ('1:1', [], 'a pinky red-brown earthworm taking a bite from the edge of a fallen orange-brown leaf; beside it a large magnifying circle (a round lens with a thin dark rim) showing a close-up of the leaf surface covered with tiny rod-shaped bacteria and fine white branching fungal threads.'),
 'g7-tunnel': ('3:4', [], 'a rectangular cut-away block of soil seen from the front: a curving worm tunnel running down through the soil, the tunnel wall lined with a thin darker brown glossy slime coating that has small white shiny highlight streaks (not blue, not water), a pinky red-brown earthworm inside the tunnel, and small round crumbly worm casts in little piles beside the tunnel and at the surface. Small leaves on top.'),
 'g8-hand': ('1:1', [], 'one open hand seen from slightly above, palm up, holding a crumbly handful of dark rich soil with two pinky red-brown earthworms in it. Only the hand and a little of the wrist, no rest of the person.'),
}
def run(name, tag):
    ar, extra, subject = JOBS[name]
    body = json.dumps({'input': {'prompt': STYLE + subject + FULL, 'image_input': extra + REFS, 'aspect_ratio': ar, 'output_format': 'png'}}).encode()
    for attempt in range(5):
        try:
            req = urllib.request.Request('https://api.replicate.com/v1/models/google/nano-banana/predictions', body,
                                         {'Authorization': f'Bearer {TOK}', 'Content-Type': 'application/json', 'Prefer': 'wait'})
            d = json.load(urllib.request.urlopen(req, timeout=300)); break
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(10 * (attempt + 1))
    while d['status'] not in ('succeeded', 'failed', 'canceled'):
        time.sleep(3); d = json.load(urllib.request.urlopen(urllib.request.Request(d['urls']['get'], headers={'Authorization': f'Bearer {TOK}'})))
    if d['status'] != 'succeeded': print(name, tag, d.get('error')); return
    o = d['output'] if isinstance(d['output'], str) else d['output'][0]
    urllib.request.urlretrieve(o, f'{HERE}/raw/{name}-{tag}.png'); print('ok', name, tag)
if __name__ == '__main__':
    tags = sys.argv[1].split(','); names = sys.argv[2:] or list(JOBS)
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(lambda nt: run(*nt), [(n, t) for n in names for t in tags]))
