"""ws15: the addition window 'frame' boxes fully enclosed the glass, so only a flat dark frame face showed.
Open each frame box's outward face into a 9 cm border ring so the recessed glass + mullions show. SAVE=1 saves."""
import bpy,bmesh,os
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data
slots=[s.material.name for s in o.material_slots]; MUL=slots.index('TZ_Cole_add_mullion_UNVERIFIED')
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
C=Vector((-107.2,-71.6,0))
seen=set(); targets=[]
for f in bm.faces:
    if f.index in seen or f.material_index!=MUL: continue
    st=[f]; c=[]; seen.add(f.index)
    while st:
        g=st.pop(); c.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen and h.material_index==MUL: seen.add(h.index); st.append(h)
    if len(c)!=9: continue
    vs={v for f in c for v in f.verts}
    zs=[v.co.z for v in vs]; ht=max(zs)-min(zs)
    if not (2.1<ht<2.5): continue
    side=[g for g in c if abs(g.normal.z)<0.1]
    big=sorted(side,key=lambda g:-g.calc_area())[:2]
    if big[0].calc_area()<2.0: continue  # mullion bars are thin
    outf=big[0]
    targets.append(outf)
print('FRAMES',len(targets))
for f in targets:
    r=bmesh.ops.inset_individual(bm,faces=[f],thickness=0.09,depth=0)
    bm.faces.remove(f) if f.is_valid else None
bm.to_mesh(me); me.update(); bm.free()
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
