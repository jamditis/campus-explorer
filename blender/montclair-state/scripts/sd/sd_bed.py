# sd: the MI planted bed under the RED HAWK wall floated up to 23 cm over the LiDAR/skirt ground at its edges
# (dark shadow gap line in the close-up). Re-seat every vertex: ground + 1.5 cm at the edge rising to +7 cm mulch crown
# 0.6 m in. Original coords saved to data/sd/bed_orig.json; REVERT=1 restores exactly.
import bpy, bmesh, json, os
from mathutils import Vector, kdtree
o=[x for x in bpy.data.objects if x.name.startswith('MI Annex west wall planted bed')][0]
me=o.data; P='data/sd/bed_orig.json'
if os.environ.get('REVERT')=='1':
    C=json.load(open(P))
    for v,c in zip(me.vertices,C): v.co=c
    me.update(); print('SD_BED reverted')
else:
    if not os.path.exists(P): json.dump([list(v.co) for v in me.vertices],open(P,'w'))
    C=json.load(open(P))
    for v,c in zip(me.vertices,C): v.co=c
    mw=o.matrix_world; inv=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    bd=[mw@v.co for v in bm.verts if v.is_boundary]; bm.free()
    kd=kdtree.KDTree(len(bd))
    for i,p in enumerate(bd): kd.insert((p.x,p.y,0),i)
    kd.balance()
    hr=o.hide_render; o.hide_viewport=True; bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    skip=('SC_','QT_','SB_')
    def ground(x,y,z0):
        org=Vector((x,y,z0+0.6))
        for _ in range(6):
            h,l,n,i,ob,_=sc.ray_cast(dg,org,Vector((0,0,-1)))
            if not h: return None
            if ob.name.startswith(skip) or ob.type!='MESH' or 'grass' in ob.name.lower(): org=l-Vector((0,0,0.001)); continue
            return l.z if abs(l.z-z0)<0.45 else None
        return None
    nm=0; dz=[]
    for v in me.vertices:
        w=mw@v.co; g=ground(w.x,w.y,w.z)
        if g is None: continue
        _,_,d=kd.find((w.x,w.y,0)); t=min(d/0.6,1.0); t=t*t*(3-2*t)
        nz=g+0.015+0.055*t; dz.append(nz-w.z); w.z=nz; v.co=inv@w; nm+=1
    o.hide_viewport=False; me.update()
    print('SD_BED moved',nm,'of',len(me.vertices),'dz min/max',round(min(dz),3),round(max(dz),3))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
