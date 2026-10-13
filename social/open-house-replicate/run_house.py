"""Run the house redraw on google/nano-banana 4 times.
  python3 run_house.py            original prompt from main on the full house -> house-raw-1..4.png
  python3 run_house.py blank      cut-paper prompt on the blank house          -> house-blank-raw-1..4.png
  python3 run_house.py free       a new house, invented; two of our photos as colour and texture reference -> house-free-raw-1..4.png"""
import os, time, sys, concurrent.futures as cf, requests
API = "https://api.replicate.com/v1"
H = {"Authorization": f"Bearer {os.environ['REPLICATE_API_TOKEN']}"}
HERE = os.path.dirname(os.path.abspath(__file__))
PROMPT = ("Redraw this house as a hand-cut paper collage illustration, like layered coloured paper and card cut with scissors, "
"with visible paper texture, slightly uneven hand-cut edges and soft shadows between the layers. Keep the composition and every "
"element in the same place: the green pitched roof, the round cream plaque in the roof gable holding the Soil Food Web Foundation "
"logo exactly as it is, the dark brown chimney on the right, the cream plank walls, the two round porthole windows with the "
"microscope photos inside them unchanged, the small OPEN sign hanging over the door, the open doorway with the photo of a laughing "
"student at a microscope inside it unchanged, the dark green door swung open to the right, and the small brown step. Colours: roof "
"Food Web Green #156826 with a darker left side, walls warm cream, chimney and frames Soil Brown #4F3433, door deep green #22371F. "
"Plain flat cream background #F4F1EA. Keep the logo, the window photos and the doorway photo as real photos, untouched. "
"No text other than the logo and the word OPEN.")

BLANK_PROMPT = ("Turn this simple vector house into a handmade cut-paper collage illustration for a children's picture book. "
"Every shape is a separate piece of real paper or thin card, cut with scissors and slightly imperfect: the roof from green "
"construction paper with visible fibres and a darker green left half, the walls from torn cream and light kraft paper with "
"overlapping torn plank strips, the chimney from brown corrugated cardboard, the door from deep green card with paper panels "
"glued on, the step from kraft cardboard. Add soft crayon and coloured pencil shading on the paper, small torn edges, and "
"gentle drop shadows under each layer so the pieces feel physical. Warm, muted, earthy, soft light. Keep the same house shape, "
"size and position, and keep every part where it is. The round plaque in the roof gable stays a plain empty cream paper circle "
"with a brown paper ring. The two round windows stay plain pale paper circles with brown paper rings. The doorway stays a plain "
"dark brown paper rectangle. The small hanging sign board stays blank. Do not add any text, letters, logos, faces, people, "
"animals or new objects. Plain flat cream background #F4F1EA.")

FREE_PROMPT = ("Invent a charming little house for the Soil Food Web open house party, made as a handmade cut-paper collage "
"for a children's picture book. Freestyle the design: a slightly crooked, hand-built cottage with personality, walls from torn "
"kraft paper and corrugated cardboard, a roof of overlapping torn green paper pieces, a round window or two, a wide open front "
"door with warm light inside, a little chimney, a few cut-paper plants and flowers growing against the walls, and soil and roots "
"just under its doorstep. Crayon and coloured pencil texture on the paper, ragged torn edges, soft drop shadows between layers so "
"it feels physical. Warm, muted, earthy palette with greens, soil browns, cream and a little mustard gold, soft light. Use the two "
"reference photos only for real colour and texture: the barn and the compost from our workshops. The house stands alone, centred, "
"on a plain flat cream background #F4F1EA. No text, no letters, no logos, no people.")

def upload(path):
    with open(path, "rb") as f:
        r = requests.post(f"{API}/files", headers=H, files={"content": (os.path.basename(path), f, "image/png")})
    r.raise_for_status(); return r.json()["urls"]["get"]

def run(i, ref, prompt=PROMPT, out_name="house-raw"):
    for attempt in range(6):
        r = requests.post(f"{API}/models/google/nano-banana/predictions", headers={**H, "Prefer": "wait=60"},
                          json={"input": {"prompt": prompt, "image_input": ref if isinstance(ref, list) else [ref], "output_format": "png"}})
        if r.status_code == 429: time.sleep(12 * (attempt + 1)); continue
        r.raise_for_status(); p = r.json(); break
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(2); p = requests.get(p["urls"]["get"], headers=H).json()
    if p["status"] != "succeeded": return f"{i}: {p['status']} {p.get('error')}"
    out = p["output"][0] if isinstance(p["output"], list) else p["output"]
    open(os.path.join(HERE, f"{out_name}-{i}.png"), "wb").write(requests.get(out, headers=H).content)
    return f"{i}: ok"

mode = sys.argv[1] if len(sys.argv) > 1 else ""
IMG = os.path.join(HERE, "..", "..", "img", "new-2026-10")
if mode == "free":
    ref = [upload(os.path.join(IMG, "ribbon-finished-piles-barn-wild-ken-hill.jpg")), upload(os.path.join(IMG, "R5A_4007.jpg"))]
    args = (FREE_PROMPT, "house-free-raw")
elif mode == "blank":
    ref = upload(os.path.join(HERE, "house-blank-reference.png")); args = (BLANK_PROMPT, "house-blank-raw")
else:
    ref = upload(os.path.join(HERE, "replicate-house-reference.png")); args = (PROMPT, "house-raw")
with cf.ThreadPoolExecutor(2) as ex:
    for res in ex.map(lambda i: run(i, ref, *args), range(1, 5)): print(res)
