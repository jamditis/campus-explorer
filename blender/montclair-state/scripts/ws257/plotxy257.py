# draw /tmp/plot257.json with PIL (x -200..-175, y 154..192), joints red
import json
from PIL import Image, ImageDraw
X0,X1,Y0,Y1,S=-200,-175,154,192,40
im=Image.new('RGB',(int((X1-X0)*S),int((Y1-Y0)*S)),'white'); d=ImageDraw.Draw(im)
f=lambda p:((p[0]-X0)*S,(Y1-p[1])*S)
for n,P in json.load(open('/tmp/plot257.json')):
    j='WS257' in n; c='red' if j else ('blue' if ('walk' in n.lower() or 'paving' in n.lower()) else 'gray')
    for poly in P: d.polygon([f(p) for p in poly],outline=c,fill='red' if j else None)
for gx in range(X0,X1+1): d.line([f((gx,Y0)),f((gx,Y1))],fill=(220,220,220))
im.save('/workspace/nj-scenes/montclair-state/scripts/ws257/plot257.png')
