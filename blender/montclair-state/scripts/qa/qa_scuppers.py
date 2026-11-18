# qa: through-wall overflow scuppers on the Dickson west-wing parapet (west face), each a small metal box 0.30 x 0.15 m
# whose bottom sits just above the roof membrane (152.50), 0.10 m proud of the brick, dark throat, faint streak below.
# Positions (every ~24 m) are invented: no roofline photo. New objects + 1 material -> REVERT=1 deletes them. UNVERIFIED.
import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
NAMES=['QA_Dickson_wing_scuppers_UNVERIFIED','QA_Dickson_wing_scupper_streaks_UNVERIFIED']; MD='QA_scupper_throat_dark_UNVERIFIED'
for n in NAMES:
    if n in bpy.data.objects:
        o=bpy.data.objects[n]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m); print('REVERTED',n)
if REV and MD in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials[MD]); print('REVERTED',MD)
YS=[float(v) for v in os.environ.get('QA_SCUP_Y','96,120,144').split(',')]
if not REV:
    mats=bpy.data.materials
    md=mats.get(MD)
    if md is None:
        md=mats.new(MD); md.use_nodes=True; b=md.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value=(0.012,0.011,0.010,1); b.inputs['Roughness'].default_value=0.9
    src=bpy.data.objects['PY_Dickson_wing_parapet_raise_UNVERIFIED']
    bm0=bmesh.new(); bm0.from_mesh(src.data); bm0.transform(src.matrix_world); bvh=BVHTree.FromBMesh(bm0)
    bm=bmesh.new(); bs=bmesh.new(); ul=bs.loops.layers.uv.new('UVMap'); n_=0
    W=0.30; H=0.15; Z0=152.53; PR=0.10; DEP=0.20
    def quad(b,P,mat=0):
        f=b.faces.new([b.verts.new(p) for p in P]); f.material_index=mat; return f
    for y in YS:
        hit=bvh.ray_cast(Vector((-200.0,y,152.70)),Vector((1,0,0)),40.0)
        if hit[0] is None: print('QA_SCUP_MISS',y); continue
        p=hit[0]; nrm=hit[1].copy(); nrm.z=0; nrm.normalize()
        if nrm.x>0: nrm=-nrm                                   # outward = towards the west
        t=Vector((-nrm.y,nrm.x,0))
        def P(u,w,z): return p+t*u+nrm*w+Vector((0,0,z-p.z))
        u0,u1=-W/2,W/2; wo,wi=PR,-DEP; za,zb=Z0,Z0+H; th=0.012
        # outer shell (sides/top/bottom) and inner liner -> a hollow throat with a lip
        for (a,b_) in (((u0,za),(u1,za)),((u1,za),(u1,zb)),((u1,zb),(u0,zb)),((u0,zb),(u0,za))):
            quad(bm,[P(a[0],wi,a[1]),P(b_[0],wi,b_[1]),P(b_[0],wo,b_[1]),P(a[0],wo,a[1])])
        U0,U1,ZA,ZB_=u0+th,u1-th,za+th,zb-th
        for (a,b_) in (((U0,ZA),(U1,ZA)),((U1,ZA),(U1,ZB_)),((U1,ZB_),(U0,ZB_)),((U0,ZB_),(U0,ZA))):
            quad(bm,[P(a[0],wo,a[1]),P(b_[0],wo,b_[1]),P(b_[0],wi,b_[1]),P(a[0],wi,a[1])])
        # mouth rim (frame between outer and inner at the mouth)
        for (A1,A2,B1,B2) in (((u0,za),(u1,za),(U1,ZA),(U0,ZA)),((u1,za),(u1,zb),(U1,ZB_),(U1,ZA)),((u1,zb),(u0,zb),(U0,ZB_),(U1,ZB_)),((u0,zb),(u0,za),(U0,ZA),(U0,ZB_))):
            quad(bm,[P(A1[0],wo,A1[1]),P(A2[0],wo,A2[1]),P(B1[0],wo,B1[1]),P(B2[0],wo,B2[1])])
        quad(bm,[P(U0,wo-0.06,ZA),P(U1,wo-0.06,ZA),P(U1,wo-0.06,ZB_),P(U0,wo-0.06,ZB_)],1)   # dark throat back
        # faint run-off streak below (shadows off), 1.6 m long, slightly wider at the bottom
        ax=0 if abs(t.x)>abs(t.y) else 1; w2=0.012
        q=[P(u0-0.02,w2,za-1.6),P(u1+0.02,w2,za-1.6),P(u1-0.02,w2,za-0.005),P(u0+0.02,w2,za-0.005)]
        vs=[bs.verts.new(x) for x in q]
        if (vs[1].co-vs[0].co).cross(vs[3].co-vs[0].co).dot(nrm)<0: vs=[vs[1],vs[0],vs[3],vs[2]]
        f=bs.faces.new(vs)
        for lp in f.loops: lp[ul].uv=(lp.vert.co[ax]*4.0, 1.0 if lp.vert.co.z>za-0.1 else 0.0)
        n_+=1; print('QA_SCUP y %.1f at (%.2f,%.2f) n (%.2f,%.2f)'%(y,p.x,p.y,nrm.x,nrm.y))
    coll=bpy.data.objects['Dickson Hall walls'].users_collection[0]
    for nm,b,ml,note,sh in ((NAMES[0],bm,['ek_coping_metal',MD],'UNVERIFIED (qa, Nov 2 2026): generic through-wall overflow scuppers at roof level, ~24 m apart; invented',True),
                           (NAMES[1],bs,['PZ_coping_drip_stain_UNVERIFIED'],'UNVERIFIED (qa): faint run-off streak under each scupper; invented',False)):
        m2=bpy.data.meshes.new(nm); b.to_mesh(m2); b.free()
        for mm in ml: m2.materials.append(mats[mm])
        o=bpy.data.objects.new(nm,m2); o['source_note']=note; o.visible_shadow=sh; coll.objects.link(o)
    bm0.free(); print('QA_SCUPPERS',n_)
