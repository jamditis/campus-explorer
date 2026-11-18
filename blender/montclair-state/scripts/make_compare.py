"""Side-by-side: Commons reference photo (CC BY-SA 4.0, Shane Fleming) vs render from CAM_ref_Morehead_west_photo."""
import sys
from PIL import Image, ImageDraw
ref, ren, out = sys.argv[1:4]
a = Image.open(ref).convert('RGB'); b = Image.open(ren).convert('RGB')
h = 720; a = a.resize((int(a.width*h/a.height), h)); b = b.resize((int(b.width*h/b.height), h))
W = Image.new('RGB', (a.width+b.width+10, h+40), 'white'); W.paste(a, (0, 40)); W.paste(b, (a.width+10, 40))
d = ImageDraw.Draw(W)
d.text((8, 12), 'Reference: Wikimedia Commons "Morehead Hall.jpg", Shane Fleming 2021, CC BY-SA 4.0', fill='black')
d.text((a.width+18, 12), 'Render: montclair_state.blend, CAM_ref_Morehead_west_photo (approximate match)', fill='black')
W.save(out, quality=90); print('saved', out)
