"""Run the house redraw on google/nano-banana 4 times. Raw outputs: house-raw-1..4.png.
Prompt is copied verbatim from social/open-house-2026-10-16/replicate-house-prompt.md on main."""
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

def upload(path):
    with open(path, "rb") as f:
        r = requests.post(f"{API}/files", headers=H, files={"content": (os.path.basename(path), f, "image/png")})
    r.raise_for_status(); return r.json()["urls"]["get"]

def run(i, ref):
    for attempt in range(6):
        r = requests.post(f"{API}/models/google/nano-banana/predictions", headers={**H, "Prefer": "wait=60"},
                          json={"input": {"prompt": PROMPT, "image_input": [ref], "output_format": "png"}})
        if r.status_code == 429: time.sleep(12 * (attempt + 1)); continue
        r.raise_for_status(); p = r.json(); break
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(2); p = requests.get(p["urls"]["get"], headers=H).json()
    if p["status"] != "succeeded": return f"{i}: {p['status']} {p.get('error')}"
    out = p["output"][0] if isinstance(p["output"], list) else p["output"]
    open(os.path.join(HERE, f"house-raw-{i}.png"), "wb").write(requests.get(out, headers=H).content)
    return f"{i}: ok"

ref = upload(os.path.join(HERE, "replicate-house-reference.png"))
with cf.ThreadPoolExecutor(2) as ex:
    for res in ex.map(lambda i: run(i, ref), range(1, 5)): print(res)
