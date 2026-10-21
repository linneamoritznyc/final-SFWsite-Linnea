"""Story images via Replicate google/nano-banana, using carousel slides as style reference."""
import base64, json, os, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
TOK = os.environ['REPLICATE_API_TOKEN']
def uri(p): return 'data:image/jpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
REFS = [uri(f'{HERE}/ref-jar.jpg'), uri(f'{HERE}/ref-block.jpg'), uri(f'{HERE}/ref-bowl.jpg')]
STYLE = ('Paint a new illustration in exactly the same style as the reference images: loose soft watercolor washes with '
         'mottled pigment and darker dried edges, thin slightly wobbly dark-brown ink outlines, muted earthy colours '
         '(soil browns, sand beige, sage green, pale aqua glass), earthworms painted pinky red-brown with a slightly darker band '
         'and fine segment lines, flat pure white background, no shadows on the background, simple educational science-book look. '
         'Absolutely no text, no letters, no numbers, no labels, no people, no hands. Subject: ')
JOBS = {
 'f1-jar': ('3:4', 'a close-up of the open top of a glass mason jar worm farm: the jar has no lid at all, just the open glass rim with screw threads. The jar is filled with layers of soil right up to just below the rim. One pinky red-brown earthworm is poking up out of the soil just inside the open rim, its head rising above the rim, wearing a tiny striped party hat on its head. Only this one worm. Show the jar from about the middle up, the bottom of the jar fading out softly. White background.'),
 'f2-book': ('4:3', 'an old open leather-bound book seen from slightly above, aged cream pages with faint blank lines suggesting text but no readable letters, one pinky red-brown earthworm resting across the open pages, centred with white space around.'),
 'f3-piano': ('4:3', 'the closed wooden lid of an upright piano seen from the front, three small terracotta clay pots of dark soil standing on the piano lid, a few small paper triangles scattered beside the pots on the lid, one pinky red-brown earthworm poking out of one pot pulling a paper triangle down into the soil, white space around.'),
 'f4-jar': ('9:16', 'a tall glass jar of soil with no lid, shown like a cut-away diagram. EXACTLY THREE worms, no more: (1) at the top, a thick layer of brown fallen leaf litter with one small bright red earthworm among the leaves; (2) in the middle, dark brown topsoil with one pale grey-pink earthworm curled into a loose spiral; (3) one long narrow dark vertical burrow running from the topsoil all the way down to the bottom of the jar, the burrow drawn as a thin dark channel in the soil, with one big long earthworm inside it whose head end (at the top) is dark reddish-brown and whose tail end (at the bottom) is pale pink. Soil fills the jar evenly below the leaves. White space around the jar.'),
 'f5-jars': ('16:9', 'three small glass jars standing in a row with space between them, each with one worm wearing a tiny party hat: left a short jar filled with fallen leaves and a small bright red worm; middle a medium jar of dark topsoil with a pale grey-pink worm; right a tall jar with one deep vertical tunnel and a big worm with a dark head and pale tail. Plain white background.'),
}
def run(name, ar, subject, tag):
    body = json.dumps({'input': {'prompt': STYLE + subject, 'image_input': REFS, 'aspect_ratio': ar, 'output_format': 'png'}}).encode()
    req = urllib.request.Request('https://api.replicate.com/v1/models/google/nano-banana/predictions', body,
                                 {'Authorization': f'Bearer {TOK}', 'Content-Type': 'application/json', 'Prefer': 'wait'})
    d = json.load(urllib.request.urlopen(req, timeout=300))
    while d['status'] not in ('succeeded', 'failed', 'canceled'):
        time.sleep(3)
        d = json.load(urllib.request.urlopen(urllib.request.Request(d['urls']['get'], headers={'Authorization': f'Bearer {TOK}'})))
    if d['status'] != 'succeeded':
        print(name, d['status'], d.get('error')); return
    out = d['output'] if isinstance(d['output'], str) else d['output'][0]
    urllib.request.urlretrieve(out, f'{HERE}/raw/{name}-{tag}.png'); print('ok', name, tag)
if __name__ == '__main__':
    tag = sys.argv[1]
    names = sys.argv[2:] or list(JOBS)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(5) as ex:
        list(ex.map(lambda n: run(n, *JOBS[n], tag), names))
