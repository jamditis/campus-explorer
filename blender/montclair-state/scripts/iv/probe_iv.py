import bpy, bmesh, math
from mathutils import Vector
import numpy as np
for o in bpy.data.objects:
    if o.type!='MESH': continue
    mats=[m.name for m in o.data.materials if m]
    if 'hn_amphi_seat_stone_blocks' not in mats: continue
    me=o.data
    print('OBJ',o.name,len(me.vertices),len(me.polygons),'mods',[(m.type,m.name) for m in o.modifiers],'mats',mats)
    print(' smooth faces',sum(p.use_smooth for p in me.polygons),'custom normals',me.has_custom_normals, 'attrs',[a.name for a in me.attributes])
    si=mats.index('hn_amphi_seat_stone_blocks')
    nz=[];tri=0;quad=0;ngon=0
    for p in me.polygons:
        if p.material_index!=si: continue
        nz.append(p.normal.z)
        n=len(p.vertices); tri+=n==3; quad+=n==4; ngon+=n>4
    nz=np.array(nz); ang=np.degrees(np.arccos(np.clip(nz,-1,1)))
    print(' seat faces',len(nz),'tri/quad/ngon',tri,quad,ngon,'tilt deg pct 50/90/99/max',np.percentile(ang,[50,90,99,100]).round(2))
    # sharp edges
    sh=me.attributes.get('sharp_edge'); 
    if sh: print(' sharp edges',sum(d.value for d in sh.data),'of',len(me.edges))
    # vertex normal tilt for seat verts
    vs=set()
    for p in me.polygons:
        if p.material_index==si: vs.update(p.vertices)
    vn=np.array([me.vertices[i].normal.z for i in vs]); va=np.degrees(np.arccos(np.clip(vn,-1,1)))
    print(' seat vert normal tilt pct 50/90/99',np.percentile(va,[50,90,99]).round(2))
