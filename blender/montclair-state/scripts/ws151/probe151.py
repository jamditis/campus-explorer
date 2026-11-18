import bpy, resource, numpy as np
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=[l for l in open('/workspace/nj-scenes/montclair-state/scripts/ws151/objnames.txt').read().split('\n') if l.startswith(('WS150_Lot9','WS148_Lot9','WS142_Lot9','WS135a_Skyline_Way','WS145_walk','WS147_walk','WS143_Freeman_E','Curbs_granite_OSM'))]
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=list(want)
for o in dst.objects:
    bpy.context.scene.collection.objects.link(o)
    print("OBJ",o.name,o.type,[ (m.type,m.name) for m in o.modifiers], [s.material.name if s.material else None for s in o.material_slots][:4])
print("RSS load",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=-72,-60,-200,-176
for o in dst.objects:
    if o.type!='MESH': continue
    oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world; c=0; zs=[]; mats={}
    for p in me.polygons:
        w=mw@p.center
        if X0<w.x<X1 and Y0<w.y<Y1:
            c+=1; zs.append(w.z); mn=o.material_slots[p.material_index].material.name if o.material_slots and o.material_slots[p.material_index].material else None; mats[mn]=mats.get(mn,0)+1
    if c: print("INBOX",o.name,c,round(min(zs),3),round(max(zs),3),mats)
    if o.name=='Curbs_granite_OSM':
        pts=[(round((mw@p.center).x,2),round((mw@p.center).y,2),round((mw@p.center).z,2)) for p in me.polygons if X0<(mw@p.center).x<X1 and Y0<(mw@p.center).y<Y1]
        pts.sort(key=lambda t:t[1]); print("CURBPTS",pts[::max(1,len(pts)//40)])
    oe.to_mesh_clear()
# top-surface grid
res=[]
for o in dst.objects: o.hide_render=False
for x in np.arange(-70,-60.9,0.5):
    row=[]
    for y in np.arange(-196,-182,0.5):
        h=bpy.context.scene.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
        row.append((round(y,1),h[4].name[:14] if h[0] else None, round(h[1].z,3) if h[0] else None))
    print("COL x",x,row)
print("RSS end",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
