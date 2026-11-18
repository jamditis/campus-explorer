# Session ec (Oct 21 2026 ~5:45 PM ET): close the notch in 'Life Hall walls' south face at the Life Hall/SCM junction
# (x 33.23-35.48, y 5.6-6.0): the LiDAR wall top drops 144.97 -> 141.45 there (jagged boundary), leaving the dark
# triangle under Life Hall's SW eave seen in eb's junction WIP. Fill: vertical faces from each open top edge in the notch
# up to the neighbour wall top (144.97 = eave underside -1 cm). Same wall line, same object (rule 4a ok).
# New faces tagged with face int attribute ec_fill=1; REVERT=1 deletes them. SAVE=1 saves.
import bpy, bmesh, os
from mathutils import Vector
o=bpy.context.scene.objects['Life Hall walls']; me=o.data; mw=o.matrix_world; inv=mw.inverted()
bm=bmesh.new(); bm.from_mesh(me)
lay=bm.faces.layers.int.get('ec_fill') or bm.faces.layers.int.new('ec_fill')
old=[f for f in bm.faces if f[lay]==1]
if old: bmesh.ops.delete(bm,geom=old,context='FACES'); print("EC_NOTCH removed",len(old))
if os.environ.get('REVERT')!='1':
    TOP=144.97
    uvl=bm.loops.layers.uv.active
    ref=None
    for f in bm.faces:
        W=[mw@v.co for v in f.verts]
        if all(32.5<w.x<33.9 for w in W) and all(5.8<w.y<6.2 for w in W) and min(w.z for w in W)>139: ref=f; break
    edges=[]
    for e in bm.edges:
        if not e.is_boundary: continue
        a,b=[mw@v.co for v in e.verts]
        if 33.2<min(a.x,b.x) and max(a.x,b.x)<35.5 and 5.5<a.y<6.1 and min(a.z,b.z)<TOP-0.05 and min(a.z,b.z)>141:
            edges.append(e)
    tops={}
    def top(v):
        w=mw@v.co
        if abs(w.z-TOP)<0.02: return v
        k=(round(w.x,3),round(w.y,3))
        if k not in tops: tops[k]=bm.verts.new(inv@Vector((w.x,w.y,TOP)))
        return tops[k]
    new=[]
    for e in edges:
        v0,v1=e.verts; t0,t1=top(v0),top(v1)
        vs=[v0,v1]+([t1] if t1 is not v1 else [])+([t0] if t0 is not v0 else [])
        if len(set(vs))<3: continue
        try: f=bm.faces.new(vs)
        except ValueError: continue
        f[lay]=1; new.append(f)
        if ref: f.material_index=ref.material_index; f.smooth=ref.smooth
    bmesh.ops.recalc_face_normals(bm,faces=new)
    # orient like ref (outward = -y-ish here)
    if ref:
        rn=(mw.to_3x3()@ref.normal)
        for f in new:
            if (mw.to_3x3()@f.normal).dot(rn)<0: f.normal_flip()
    # UVs: affine fit (s,z)->uv from ref face
    if ref and uvl:
        import numpy as np
        d=Vector((-0.97,0.23,0)).normalized()
        P=[]; U=[]
        for l in ref.loops:
            w=mw@l.vert.co; P.append([w.dot(d),w.z,1]); U.append(list(l[uvl].uv))
        M,_,_,_=np.linalg.lstsq(np.array(P),np.array(U),rcond=None)
        for f in new:
            for l in f.loops:
                w=mw@l.vert.co; l[uvl].uv=tuple(np.array([w.dot(d),w.z,1])@M)
    print("EC_NOTCH edges",len(edges),"new faces",len(new),"ref",ref.index if ref else None)
bm.to_mesh(me); me.update(); bm.free()
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print("EC_SAVED")
