# ws33: terrain poked up to the drive surface at x -7..-3.5, y -47..-43 (green patch on the asphalt). Seat terrain >=6 cm under Roads_OSM in the dock box; strip grass points over the drive.
import bpy,bmesh
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
R=bpy.data.objects['Roads_OSM'];T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
re_=R.evaluated_get(dg); ri=R.matrix_world.inverted()
def rz(x,y):
    ok,hp,_,_=re_.ray_cast(ri@Vector((x,y,200)),(ri.to_3x3()@Vector((0,0,-1))).normalized())
    return (R.matrix_world@hp).z if ok else None
print('terrain mods',[m.type for m in T.modifiers])
tm=T.matrix_world; ti=tm.inverted(); n=0
for v in T.data.vertices:
    p=tm@v.co
    if not(-9<p.x<1 and -52<p.y<-26): continue
    zs=[rz(p.x+dx,p.y+dy) for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5))]
    zs=[z for z in zs if z is not None]
    if len(zs)<5: continue   # vertex fully under the drive only (keep verges untouched)
    lim=min(zs)-0.06
    if p.z>lim:
        v.co=ti@Vector((p.x,p.y,lim)); n+=1
T.data.update(); print('terrain verts seated under drive',n)
for name in ('Lawn_worn_edge_along_walks','Lawn_grass_instanced (3g)','dS_grass_ccom_points'):
    o=bpy.data.objects.get(name)
    if not o or o.type!='MESH': continue
    m=o.matrix_world; b=bmesh.new(); b.from_mesh(o.data); kill=[]
    for v in b.verts:
        p=m@v.co
        if not(-9<p.x<1 and -52<p.y<-26): continue
        z=rz(p.x,p.y)
        if z is not None and abs(z-p.z)<0.6: kill.append(v)
    bmesh.ops.delete(b,geom=kill,context='VERTS'); b.to_mesh(o.data); b.free(); o.data.update(); print('removed over drive',name,len(kill))
