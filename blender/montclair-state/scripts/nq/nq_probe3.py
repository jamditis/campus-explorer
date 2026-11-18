import bpy, mathutils, bmesh
from bpy_extras.view3d_utils import region_2d_to_vector_3d
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Roof_vent']; me=o.data
print('RV',len(me.vertices),len(me.polygons),[m.name for m in o.modifiers],[s.material.name if s.material else None for s in o.material_slots], o.data.library)
bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
isl=[]; seen=set()
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; comp=[]; seen.add(v.index)
    while st:
        x=st.pop(); comp.append(x.co.copy())
        for e in x.link_edges:
            w=e.other_vert(x)
            if w.index not in seen: seen.add(w.index); st.append(w)
    c=sum(comp,mathutils.Vector())/len(comp); isl.append((c,min(p.z for p in comp)))
for c,zmin in isl:
    if -40<c.x<40 and -30<c.y<45: print('ISL',tuple(round(a,2) for a in c),round(zmin,2))
cam=bpy.data.objects['NP_CAM_aerial_cutaway_studio_atrium_oblique']
fr=cam.data.view_frame(scene=sc)
for px,py in ((500,430),(520,320),(560,500),(632,48),(410,355),(735,372),(515,445)):
    u=px/1024; v=1-py/576
    tl,tr,br,bl=[cam.matrix_world@p for p in fr]  # view_frame order: tr, br, bl, tl
    tr,br,bl,tl=[cam.matrix_world@p for p in fr]
    pt=bl+(br-bl)*u+(tl-bl)*v; d=(pt-cam.matrix_world.translation).normalized()
    hit,loc,n,i,ob,m=sc.ray_cast(dg,cam.matrix_world.translation,d)
    print('PIX',px,py,hit and tuple(round(a,2) for a in loc), ob.name if hit else None)
