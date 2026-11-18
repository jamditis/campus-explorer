# pr: second pass of pq_oldtop with a 13 cm (was 6 cm) cover tolerance, for old-wall stubs whose sloped tops stand 5-7 cm
# in front of the tier walls (right edge of the PO close-up). Original z in pr_z0; REVERT=1 restores. UNVERIFIED.
# pq: the old LiDAR 'Feliciano School of Business walls' have sloped/stepped top edges that poke 3 cm in front of the
# straight tier walls (diagonal grey lines). Each old top vertex that has a PN tier wall within 8 cm behind it is lowered
# down the wall as far as the tier wall keeps covering it (0.25 m steps, never below the lowest covered sample).
# Original z in point attr pr_z0; REVERT=1 restores. UNVERIFIED.
import bpy, os, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
o=bpy.data.objects['Feliciano School of Business walls']; me=o.data; mw=o.matrix_world; mi=mw.inverted()
a=me.attributes.get('pr_z0')
if REV:
    if a:
        for v in me.vertices: v.co.z=a.data[v.index].value
        me.attributes.remove(a); me.update()
    print('PR_OLDTOP reverted'); 
else:
    tiers=[t for t in bpy.data.objects if t.name.startswith('PN_Feliciano_tier_') and 'windows' not in t.name]
    V=[];F=[]
    for t in tiers:
        b=len(V); V+=[t.matrix_world@v.co for v in t.data.vertices]; F+=[[b+i for i in p.vertices] for p in t.data.polygons]
    bvh=BVHTree.FromPolygons(V,F)
    if a is None:
        a=me.attributes.new('pr_z0','FLOAT','POINT')
        for v in me.vertices: a.data[v.index].value=v.co.z
    # per vertex: outward horizontal normals of adjacent vertical faces
    vn={}
    for p in me.polygons:
        n=mw.to_3x3()@p.normal
        if abs(n.z)>0.3: continue
        n.z=0
        if n.length<1e-6: continue
        n.normalize()
        for i in p.vertices: vn.setdefault(i,[]).append(n)
    zs=[mw@v.co for v in me.vertices]; zmax={}
    moved=0; drop=0
    def covered(pt,n):
        # tier wall within 8 cm on either side (normals are inconsistent): probe both directions
        for d in (n,-n):
            h=bvh.ray_cast(pt+d*0.13,-d,0.28)
            if h[0] is not None: return True
        return False
    for i,ns in vn.items():
        w=mw@me.vertices[i].co
        if w.z<141.0: continue
        # only top vertices: highest among the vertex's faces' verts at this xy (no vertex above within 0.2 m xy)
        n=ns[0]
        if not covered(w,n): continue
        z=w.z; zz=z
        while zz-0.25>140.0 and covered(Vector((w.x,w.y,zz-0.25)),n): zz-=0.25
        if zz<z-0.01:
            w2=Vector((w.x,w.y,zz)); me.vertices[i].co=mi@w2; moved+=1; drop=max(drop,z-zz)
    me.update(); print('PR_OLDTOP moved',moved,'maxdrop',round(drop,2))
if not REV:
    # pass 2: old-wall tops that stand up to 1.5 m ABOVE the tier wall behind them (parapet-like stubs above a lower
    # tier's roof, e.g. x -222..-219.9 / y 218.7 at 157.4 over tier 156.6): drop them to the highest covered height.
    m2=0
    for i,ns in vn.items():
        w=mw@me.vertices[i].co
        if w.z<141.0: continue
        n=ns[0]
        if covered(w,n): continue
        zz=w.z; ok=None
        while zz>w.z-1.5:
            zz-=0.1
            if covered(Vector((w.x,w.y,zz)),n): ok=zz; break
        if ok is not None:
            me.vertices[i].co=mi@Vector((w.x,w.y,ok-0.02)); m2+=1
    me.update(); print('PR_OLDTOP pass2 moved',m2)
