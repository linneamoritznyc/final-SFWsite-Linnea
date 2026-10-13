#!/bin/bash
# preview.sh <pptx> <out.png> : LibreOffice render + contact sheet
set -e
d=$(mktemp -d); cp "$1" $d/x.pptx
timeout 500 soffice --headless --norestore -env:UserInstallation=file:///tmp/lo_prof --convert-to pdf --outdir $d $d/x.pptx >/dev/null 2>&1
python3 - "$d/x.pdf" "$2" <<'PY'
import sys, pymupdf
from PIL import Image
d=pymupdf.open(sys.argv[1]); ims=[]
for p in d:
    pix=p.get_pixmap(dpi=max(10,int(96*360/ (p.rect.width*96/72)))); ims.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
w,h=ims[0].size; sheet=Image.new('RGB',(w*4+50,h*3+40),'#333')
for i,im in enumerate(ims): sheet.paste(im,(10+(i%4)*(w+10),10+(i//4)*(h+10)))
sheet.save(sys.argv[2]); print(sheet.size)
PY
