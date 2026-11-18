# ws211c: swap the fn_lot_asphalt paint mask (ws211a tiles) for the ortho stall-by-stall layout (ws211c tiles)
import bpy
def _f211c():
    m=bpy.data.materials['fn_lot_asphalt']; N=m.node_tree.nodes
    for nd in [nd for nd in N if nd.name.startswith('ws211_')]: N.remove(nd)
    for im in [im for im in bpy.data.images if im.name.startswith('ws211_mask_tile_')]: bpy.data.images.remove(im)
    print('F211 ws211a mask nodes/images removed',flush=True)
_f211c(); del _f211c
TILEJSON='/workspace/nj-scenes/montclair-state/data/ws211c_mask_tiles.json'
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws211/fix211a.py').read())
