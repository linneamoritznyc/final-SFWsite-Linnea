"""Remove backgrounds from the chosen raw outputs with rembg and save trimmed PNG cutouts."""
from rembg import remove, new_session
from PIL import Image
import sys
sess=new_session('isnet-general-use')
pick={'paper-triangles':'t1','midden':'t1','worm-stone':'t1','piano-pots':'t2','burrow-cross-section':'t1',
      'drilosphere-circle':'t1','root-in-burrow':'t1','spade-cut':'t1','three-worms':'t1'}
for n,t in pick.items():
    im=Image.open(f'raw/{n}-{t}.png').convert('RGB')
    out=remove(im,session=sess,post_process_mask=True)
    a=out.split()[3].point(lambda v:0 if v<12 else v); out.putalpha(a)
    out=out.crop(out.getbbox()); out.save(f'cutouts/{n}.png'); print(n,out.size)
