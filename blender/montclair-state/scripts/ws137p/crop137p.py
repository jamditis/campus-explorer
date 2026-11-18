import sys
from PIL import Image, ImageDraw
X0,X1,Y0,Y1=-185,-85,-305,-240
cx0,cx1,cy0,cy1=[float(v) for v in sys.argv[1:5]]; src=sys.argv[5]; out=sys.argv[6]; S=8
im=Image.open(src)
box=((cx0-X0)*S,(Y1-cy1)*S,(cx1-X0)*S,(Y1-cy0)*S)
c=im.crop(tuple(int(b) for b in box)); k=int(sys.argv[7]) if len(sys.argv)>7 else 2
c=c.resize((c.width*k,c.height*k),Image.NEAREST); c.save(out)
