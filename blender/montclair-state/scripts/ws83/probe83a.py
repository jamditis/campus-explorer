import bpy,bmesh
from mathutils import Vector
FP=bpy.data.objects['Footpaths_OSM']; mw=FP.matrix_world
print('P83 FP mods',[m.type+':'+m.name for m in FP.modifiers],'mats',[m.name for m in FP.data.materials if m])
b=bmesh.new(); b.from_mesh(FP.data); b.transform(mw)
fs=[f for f in b.faces if -226<f.calc_center_median().x<-214 and -134<f.calc_center_median().y<-104]
print('P83 faces',len(fs))
S=set(fs); bes=[]
for f in fs:
    for e in f.edges:
        lf=[g for g in e.link_faces]
        if len(lf)==1:
            a,c=e.verts; bes.append(((a.co.x+c.co.x)/2,(a.co.y+c.co.y)/2,(a.co.z+c.co.z)/2,a.co.x,a.co.y,c.co.x,c.co.y))
bes.sort(key=lambda q:q[1])
for q in bes: print('P83 BE %.2f %.2f %.3f  (%.2f,%.2f)-(%.2f,%.2f)'%q)
zs=[v.co.z for f in fs for v in f.verts]; print('P83 zr',min(zs),max(zs))
print('P83 curbmats',[m.name for m in bpy.data.materials if 'curb' in m.name.lower()][:30])
print('P83 curbobs',[o.name for o in bpy.data.objects if 'curb' in o.name.lower()][:40])
L=bpy.data.objects['WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges']
xs=[v.co.x for v in L.data.vertices]; print('P83 lane x',min(xs),max(xs))
