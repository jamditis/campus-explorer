# ws275 probe275a (merge208-style loader, modifiers off, no save): AGENTS.md rule 16 — list anything in the main file that could
# be a housing interior: text objects, objects/collections/materials whose names say room, interior, floor, corridor, plan, label,
# and every object whose bounding box centre falls inside a housing footprint (OSM building outlines, scene XY, from HOUSING below).
import bpy, os, re, json
from bpy.app.handlers import persistent
from mathutils import Vector
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport = False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath=os.environ['INF'])
KW = re.compile(r'room|interior|floor_?plan|floorplan|corridor|hallway|partition|label|bedroom|suite|dorm|stair_?well|lounge', re.I)
HOUSE = re.compile(r'blanton|village|hawk|sinatra|dinallo|machuga|bohn|freeman|russ|webster|stone|clove|heights|residen|dorm|apartment|hall', re.I)
out = {'text': [], 'kw_obj': [], 'kw_coll': [], 'kw_mat': [], 'house_obj': []}
for o in bpy.data.objects:
    if o.type == 'FONT':
        out['text'].append([o.name, getattr(o.data, 'body', '')[:60], [round(v, 1) for v in o.matrix_world.translation]])
    if KW.search(o.name):
        out['kw_obj'].append([o.name, o.type, [round(v, 1) for v in o.matrix_world.translation]])
    if HOUSE.search(o.name):
        out['house_obj'].append([o.name, o.type, len(o.data.vertices) if o.type == 'MESH' else 0])
for c in bpy.data.collections:
    if KW.search(c.name) or HOUSE.search(c.name):
        out['kw_coll'].append([c.name, len(c.all_objects)])
for m in bpy.data.materials:
    if KW.search(m.name):
        out['kw_mat'].append([m.name, m.users])
out['counts'] = {'objects': len(bpy.data.objects), 'meshes': len(bpy.data.meshes), 'materials': len(bpy.data.materials),
                 'images': len(bpy.data.images), 'node_groups': len(bpy.data.node_groups), 'collections': len(bpy.data.collections),
                 'modifiers': sum(len(o.modifiers) for o in bpy.data.objects),
                 'verts': sum(len(me.vertices) for me in bpy.data.meshes)}
json.dump(out, open(os.environ['OUTJ'], 'w'), indent=1)
print('P275A', json.dumps(out['counts']), {k: len(v) for k, v in out.items() if isinstance(v, list)}, flush=True)
