import bpy, bmesh, math
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Footpaths_OSM','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS74_cogen_lot_asphalt_ortho2020_UNVERIFIED_edges']
with bpy.data.libraries.load(p) as (s,d): d.objects=names
for o in d.objects:
    bpy.context.scene.collection.objects.link(o)
print("ALLOBJ",[o.name for o in bpy.data.objects])
dg=bpy.context.evaluated_depsgraph_get()
for o in d.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print("BB",o.name[:30],len(o.data.vertices),[round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)])
f=bpy.data.objects['Footpaths_OSM']
print("MODS",[(m.name,m.type,getattr(m,'node_group',None) and m.node_group.name) for m in f.modifiers])
for m in f.modifiers:
    if m.type=='NODES':
        for k in m.keys(): 
            v=m[k]; print("  IN",m.name,k,getattr(v,'name',v) if not hasattr(v,'__len__') or isinstance(v,str) else '')
me=f.evaluated_get(dg).to_mesh(); mw=f.matrix_world
print("EVAL",len(me.vertices),len(me.polygons))
bad=[]
for pl in me.polygons:
    c=mw@pl.center
    if -215<c.x<-120 and -110<c.y<-20:
        n=(mw.to_3x3()@pl.normal).normalized()
        if n.z<0.8: bad.append((round(c.x,1),round(c.y,1),round(c.z,2),round(n.z,2),pl.area))
print("STEEP",len(bad))
for b in sorted(bad)[:80]: print(" ",b)
# source mesh in region
src=[mw@v.co for v in f.data.vertices]
r=[v for v in src if -215<v.x<-120 and -110<v.y<-20]
print("SRCREG",len(r), r[:5])
