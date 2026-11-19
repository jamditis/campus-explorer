# ws221a: rename the packed ws219 paint-mask images so tools/web-export (regex ws\d+[a-z]?_mask_tile_) exports their paint.
# Packed; filepath left alone (re-pathing a packed image triggers a re-pack). Tile lists: data/ws219{a,b,z}_mask_tiles.json.
import bpy
M={'ws219a_mask_WS179_0.png':'ws219a_mask_tile_0.png','ws219a_mask_WS179_1.png':'ws219a_mask_tile_1.png',
   'ws219b_mask_WS130_2.png':'ws219b_mask_tile_2.png','ws219b_mask_WS135a_3.png':'ws219b_mask_tile_3.png',
   'ws219b_mask_WS138a_4.png':'ws219b_mask_tile_4.png','ws219z_mask_rhd_se_crosswalk.png':'ws219z_mask_tile_0.png'}
n=0
for a,b in M.items():
    im=bpy.data.images.get(a)
    if im: im.name=b; n+=1
    print('F221A',a,'->',b if im else 'MISSING',flush=True)
if n!=len(M): raise SystemExit('F221A missing images')
