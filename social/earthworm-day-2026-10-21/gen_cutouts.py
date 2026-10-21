"""Generate cut-paper collage cutouts with Replicate (flux-2-pro), then remove backgrounds with rembg."""
import os,json,time,urllib.request,sys,threading
TOK=os.environ['REPLICATE_API_TOKEN']
def post(url,data=None):
    req=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers={'Authorization':'Bearer '+TOK,'Content-Type':'application/json','Prefer':'wait=60'})
    return json.load(urllib.request.urlopen(req,timeout=300))
STYLE=("Cut-paper collage object, made of real layered textured paper with visible paper fibres and torn and cut edges, soft natural light, "
       "a single isolated object centred on a plain flat uniform light grey background, nothing else in the frame, no text, no letters, no labels, no frame, no border. ")
P={
'paper-triangles':("Small cream paper triangles being dragged tip first into a single earthworm burrow hole in a small round patch of green lawn, a few triangles already half sunk into the hole","1:1"),
'midden':("A small worm midden: a little tuft of brown and ochre fallen leaves standing upright, pulled tip first into a small worm hole in a patch of dark soil and short grass","1:1"),
'worm-stone':("A round flat grey stone with a thin metal measuring peg standing upright in its centre, the stone half sunk into a small patch of green grass and soil","1:1"),
'piano-pots':("Three small terracotta clay flower pots filled with dark soil standing in a row on top of a small black upright piano, the piano keyboard with white and black keys clearly visible below the pots","4:3"),
'burrow-cross-section':("A tall vertical cross-section slab of layered soil, light brown topsoil grading to dark brown subsoil, with one long vertical earthworm burrow running from top to bottom, the burrow walls lined darker, a large pink-brown earthworm inside the burrow","9:16"),
'drilosphere-circle':("A perfectly round circular magnified view of an earthworm burrow wall, clean flat scientific illustration in BioRender style, pale brown soil background inside the circle, small rod-shaped terracotta bacteria, thin white branching fungal threads, one soft rounded amoeba, one small flagellate with a whip tail, one slim pale nematode; everything clearly inside the circle","1:1"),
'root-in-burrow':("A tall narrow cross-section slab of brown soil with a vertical earthworm burrow, a slender white plant root with fine root hairs growing straight down along the inside of the burrow wall","9:16"),
'spade-cut':("A steel garden spade blade with a short wooden handle stub, pushed straight down into a block of brown soil, slicing through a round earthworm burrow tunnel visible in the cut face of the soil","1:1"),
'three-worms':("Three earthworms side by side for comparison, each in its own small block of soil: left a small bright red earthworm in a little pile of leaf litter, middle a pale pinkish-grey earthworm in light brown topsoil, right a large dark brown earthworm in a tall dark soil block with a deep vertical burrow","16:9"),
}
def run(name,tag):
    prompt,ar=P[name]
    for model in ('black-forest-labs/flux-2-pro','black-forest-labs/flux-1.1-pro'):
        try:
            inp={'prompt':STYLE+prompt,'aspect_ratio':ar,'output_format':'png','safety_tolerance':2}
            p=post(f'https://api.replicate.com/v1/models/{model}/predictions',{'input':inp})
            while p['status'] not in ('succeeded','failed','canceled'):
                time.sleep(3); p=post(p['urls']['get'])
            print(name,tag,model,p['status'],p.get('error'),flush=True)
            if p['status']=='succeeded':
                u=p['output'] if isinstance(p['output'],str) else p['output'][0]
                urllib.request.urlretrieve(u,f'raw/{name}-{tag}.png'); return
        except Exception as e: print(name,model,'err',e,flush=True)
if __name__=='__main__':
    tag=sys.argv[1]; names=sys.argv[2:] or list(P)
    th=[threading.Thread(target=run,args=(n,tag)) for n in names]
    for t in th: t.start(); time.sleep(11)
    for t in th: t.join()
