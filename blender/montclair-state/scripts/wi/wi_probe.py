import bpy, json
from mathutils import Vector
out={}
names=['WG_Bohn_W_door_landing_slab_UNVERIFIED','WD_walk_1132693523','WG_Bohn_W_door_cheek_wall_N_UNVERIFIED','WG_Bohn_W_door_cheek_wall_S_UNVERIFIED']
for o in bpy.data.objects:
    if 'W_door' in o.name or '1132693523' in o.name:
        names.append(o.name)
for n in dict.fromkeys(names):
    o=bpy.data.objects.get(n)
    if not o: out[n]='MISSING'; continue
    d={'type':o.type,'hide_render':o.hide_render,'loc':list(o.location),'mods':[(m.name,m.type) for m in o.modifiers]}
    if o.type=='MESH':
        me=o.data; mw=o.matrix_world
        vs=[mw@v.co for v in me.vertices]
        d['nv']=len(vs)
        d['bb']=[min(v.x for v in vs),max(v.x for v in vs),min(v.y for v in vs),max(v.y for v in vs),min(v.z for v in vs),max(v.z for v in vs)]
        d['mats']=[m.name if m else None for m in me.materials]
        d['uv']=[u.name for u in me.uv_layers]
        if 'walk' in n:
            # verts near pad x 213-217
            d['near_pad']=[tuple(round(c,3) for c in v) for v in vs if v.x>211.5]
    out[n]=d
for mn in ['QT_walk_concrete_joints_UNVERIFIED','TJ_door_frame_UNVERIFIED']:
    m=bpy.data.materials.get(mn)
    if m and m.node_tree:
        out['MAT_'+mn]={'users':m.users,'nodes':[(nd.name,nd.type) for nd in m.node_tree.nodes]}
json.dump(out,open('data/wi/probe.json','w'),indent=1,default=str)
print('OK')
