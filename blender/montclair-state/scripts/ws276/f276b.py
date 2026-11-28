# ws276 f276b (merge208 CHAIN, on ws276a): give the Sprague roof material its published web colour back (Codex review, PR ws276).
# The release copy (ws244/strip244_lowmem.py) drops ortho images and feeds each such material a stand-in RGB node; on
# 'North_roof_ortho2020.002' (Sprague L0, L1 main, SW raised block) that is the default (0.20, 0.20, 0.18) at HSV value 0.6, so
# the t_-1_0 export from this release-derived file flattened the roof to 0.20 grey. The published t_-1_0 (ws251b, from Void's
# file with the ortho image) has it at (0.4595, 0.4755, 0.4271), HSV value 0.95: set the RGB node and value to that.
import bpy
TAG = 'F276B'
m = bpy.data.materials['North_roof_ortho2020.002']
N = m.node_tree.nodes
rgb = [n for n in N if n.type == 'RGB']; hsv = [n for n in N if n.type == 'HUE_SAT']
if len(rgb) != 1 or len(hsv) != 1 or not hsv[0].inputs['Color'].is_linked or hsv[0].inputs['Color'].links[0].from_node != rgb[0]:
    raise SystemExit(TAG + ' refused: node layout is not the strip244 stand-in (one RGB into one Hue/Saturation/Value)')
old = [round(v, 4) for v in rgb[0].outputs[0].default_value], round(hsv[0].inputs['Value'].default_value, 3)
rgb[0].outputs[0].default_value = (0.4595, 0.4755, 0.4271, 1.0)
hsv[0].inputs['Value'].default_value = 0.95
users = [o.name[:40] for o in bpy.data.objects if o.type == 'MESH' and any(s.material == m for s in o.material_slots)]
print(TAG, m.name, 'rgb/value', old, '->', [0.4595, 0.4755, 0.4271, 1.0], 0.95, 'objects', users, flush=True)
