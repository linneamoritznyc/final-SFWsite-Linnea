"""Painted backgrounds for the anniversary cover, in the style of Linnea Moritz's own cubist painting
(style-ref-linnea-moritz.jpg, her work, used with her direction). google/nano-banana, 4 runs, raw outputs kept.
  python3 social/turns-one-cover/painted-gen/generate.py
"""
import os, sys, concurrent.futures as cf, requests
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
import soil_cutouts as sc

PROMPT = ("Paint a new oil painting in exactly the style of this reference painting: soft cubist planes that interlock and "
"overlap, each plane modelled from light to shade with smooth oil brushwork, thin pale edges between planes, nested circles, "
"pointed leaf shapes, a warm muted palette of dove grey, lilac, mauve, dusty rose, peach, ochre and butter yellow with a few "
"saturated accents of terracotta and coral, visible canvas texture. Do not copy the reference composition or its figure. "
"Subject: Mother Earth resting peacefully. The lower half is a large, gently rounded hill of rich soil, soft and at rest, painted as layered cubist planes of brown, umber and terracotta soil, with round soil aggregates, two "
"earthworms curled at rest and fine roots inside it. Cover crops (clover, vetch with small purple flowers, young green "
"shoots) grow softly from the top of the soil. Above, a large soft glowing pale arch of light at the centre, like a halo, "
"calm and luminous. A few small purple flowers. The mood is peaceful, restful and quietly joyful. Leave the inside of the "
"glowing arch empty and pale, with no objects, so text can be placed there later. No text, no letters, no signature, no people.")


def one(i, ref):
    if os.path.exists(os.path.join(HERE, f"raw-{i}.png")): return i
    try:
            out = sc.predict(f"{sc.API}/models/google/nano-banana/predictions",
                         {"input": {"prompt": PROMPT, "image_input": [ref], "aspect_ratio": "4:5", "output_format": "png"}})
    except RuntimeError as e:
        return f"{i} failed: {e}"
    open(os.path.join(HERE, f"raw-{i}.png"), "wb").write(requests.get(out, headers=sc.H).content)
    return i

ref = sc.upload(os.path.join(HERE, "style-ref-linnea-moritz.jpg"))
with cf.ThreadPoolExecutor(2) as ex:
    for i in ex.map(lambda i: one(i, ref), range(1, 5)): print("raw", i)
