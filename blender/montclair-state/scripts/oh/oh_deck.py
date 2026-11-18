# oh: the grey sawtooth was the og membrane deck (flat, z 151.37, inset 3 m) poking out of the undulating LiDAR tile slope.
# Hide og deck + coping (not deleted) and rebuild both at inset 5 m (data/oh/schmitt_deck_inset5_oh.json), same z/materials.
# REVERT=1 removes the OH copies and unhides og.
import bpy, bmesh, json, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
OGD=bpy.data.objects['OG_Schmitt_roof_membrane_deck']; OGC=bpy.data.objects['OG_Schmitt_mansard_coping_cap']
COL=bpy.data.collections['OH_Schmitt_cams_20261031oh']
for n in ('OH_Schmitt_roof_membrane_deck_inset5','OH_Schmitt_coping_cap_inset5'):
    o=bpy.data.objects.get(n)
    if o: me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
for o in (OGD,OGC): o.hide_render=False; o.hide_viewport=False; o.hide_set(False)
if not REV:
    ring=json.load(open('data/oh/schmitt_deck_inset5_oh.json'))[0][0]; ZD=151.37
    bm=bmesh.new(); fv=[bm.verts.new((x,y,ZD)) for x,y in ring]; f=bm.faces.new(fv); f.normal_update()
    if f.normal.z<0: f.normal_flip()
    me=bpy.data.meshes.new('OH_Schmitt_roof_membrane_deck_inset5'); bm.to_mesh(me); me.materials.append(OGD.data.materials[0])
    o=bpy.data.objects.new(me.name,me); COL.objects.link(o)
    bm=bmesh.new(); Z=Vector((0,0,1))
    for i in range(len(ring)):
        a=Vector((*ring[i],0)); b=Vector((*ring[(i+1)%len(ring)],0)); d=b-a; L=d.length
        if L<0.05: continue
        X=d/L; Y=Z.cross(X); c=(a+b)/2; hx=(L+0.30)/2; hy=0.15
        vs=[bm.verts.new(c+X*sx*hx+Y*sy*hy+Vector((0,0,z))) for z in (151.28,151.47) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
        for q in ((0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bm.faces.new([vs[k] for k in q])
    me=bpy.data.meshes.new('OH_Schmitt_coping_cap_inset5'); bm.to_mesh(me); me.materials.append(OGC.data.materials[0])
    o=bpy.data.objects.new(me.name,me); COL.objects.link(o)
    for o in (OGD,OGC): o.hide_render=True; o.hide_viewport=True; o.hide_set(True)
    print('deck verts',len(ring))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
