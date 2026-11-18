# ws143 (#50 part 2): Freeman E concrete band between the building face and the Lot 9 W curb (2023 LiDAR class-2 intensity 10-13k,
# x = xw(y)-5.3 .. xw(y)-0.15, y -178.45 .. -203.2). Built only if the scene has no paving there already (probe below).
import bpy, bmesh, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
SKIP=('Terrain','Roads_OSM','Footpaths_OSM','UA_','WS110_ground','WS113_terrain','WS114_terrain','WS133b_','WS134_ground','Context_skirt','WS142_','WS143_','WS113_paving_tops_proxy')
hits=[]
for y in (-181,-185,-190,-195,-200):
    x=xw(y)-2.5
    ok,loc,nor,idx,ob,mx=sc.ray_cast(dg,Vector((x,y,lz(x,y)+3.0)),Vector((0,0,-1)))
    hits.append((y,ob.name if ob else None,round(loc.z-lz(x,y),2) if ok else None))
print('BANDPROBE',hits)
paved=[h for h in hits if h[1] and not h[1].startswith(SKIP) and h[2] is not None and abs(h[2])<0.4]
if len(paved)>=3:
    print('BAND SKIPPED: already modelled by',set(h[1] for h in paved))
else:
    bm=bmesh.new(); rows=[]
    YS=list(np.arange(-178.45,-203.2,-0.5))+[-203.2]
    for y in YS:
        xa=xw(y)-5.3; xb=xw(y)-0.15; xs=np.linspace(xa,xb,12)
        rows.append([bm.verts.new((x,y,lz(x,y)+0.10)) for x in xs])
    for k in range(len(rows)-1):
        for i in range(11): bm.faces.new((rows[k][i],rows[k][i+1],rows[k+1][i+1],rows[k+1][i]))
    for f in bm.faces:
        f.normal_update()
        if f.normal.z<0: f.normal_flip()
    me=bpy.data.meshes.new('WS143_Freeman_E_concrete_band_LiDAR2023int_UNVERIFIEDjoints'); bm.to_mesh(me); bm.free(); me.materials.append(con)
    uv=me.uv_layers.new(name='UVMap')
    for lp in me.loops:
        p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.5,p.y*0.5)
    bo=OB.new(me.name,me); col.objects.link(bo); print('BAND built faces',len(me.polygons))
