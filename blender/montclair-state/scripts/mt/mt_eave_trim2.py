# mt pass 2: the downspout + drip-streak decals that hung off the removed eave strip go entirely (no gutter feeds them now).
import bpy, bmesh
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
U0,U1=3.197,10.397
for nm in ['Downspouts (3f)','Eave drip / moss streaks on stucco (3g)']:
    o=bpy.data.objects[nm]; mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(o.data)
    # connected pieces: delete whole islands whose centre lies in the strip
    bm.faces.ensure_lookup_table(); seen=set(); kill=[]
    for f in bm.faces:
        if f.index in seen: continue
        isl=[]; st=[f]; seen.add(f.index)
        while st:
            g=st.pop(); isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); st.append(h)
        c=sum((mw@g.calc_center_median() for g in isl),Vector())/len(isl)
        if U0-0.1<c.dot(t)<U1+0.1 and 21.6<c.dot(n)<23.7 and c.z<148.7: kill+=isl
    print('ISLAND_TRIM',nm,len(kill))
    if kill: bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); o.data.update()
    bm.free()
bpy.ops.wm.save_mainfile(); print('SAVED')
