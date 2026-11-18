"""Side-by-side: Joe's photo (left) vs Blender render (right), same height, labels. 2026-10-14x."""
import sys
from PIL import Image, ImageDraw, ImageFont
ref, ren, out, lab_l, lab_r = sys.argv[1:6]
H = int(sys.argv[6]) if len(sys.argv) > 6 else 720
a = Image.open(ref).convert('RGB'); b = Image.open(ren).convert('RGB')
a = a.resize((int(a.width * H / a.height), H), Image.LANCZOS); b = b.resize((int(b.width * H / b.height), H), Image.LANCZOS)
W = Image.new('RGB', (a.width + b.width + 12, H + 44), (255, 255, 255))
W.paste(a, (0, 44)); W.paste(b, (a.width + 12, 44))
d = ImageDraw.Draw(W)
try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except Exception: f = None
d.text((8, 12), lab_l, fill='black', font=f); d.text((a.width + 20, 12), lab_r, fill='black', font=f)
W.save(out, quality=90); print('saved', out, W.size)
