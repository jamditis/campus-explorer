# on: Schmitt low-block walls (faces with top 145.3-145.9, x -24..-18, y 110..117) stop ~3.5-4.5 m under the Schmitt LiDAR roof (149.4-150.0): open band shows the dark window boxes. Add a stucco infill band from each wall top to 149.06 (main-block wall top), 0.2 m thick, inward. REVERT=1 removes it.
import bpy, bmesh, os, sys
from mathutils import Vector
NAME='ON_Schmitt_low_block_wall_infill_to_roof_UNVERIFIED'; COL='ON_Schmitt_shard_fix_wall_infill_20261031on'
def rm():
    o=bpy.data.objects.get(NAME)
    if o: me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
    c=bpy.data.collections.get(COL)
    if c and not c.objects: bpy.data.collections.remove(c)
rm()
if os.environ.get('REVERT')=='1':
    print('ON_INFILL_REVERTED')
else:
    w=bpy.data.objects['Schmitt Hall walls']; me=w.data; M=w.matrix_world
    ctr=Vector((-21.0,113.0)); TOP=149.06
    from mathutils.bvhtree import BVHTree
    ro=bpy.data.objects['Schmitt Hall roof (LiDAR)']; dg=bpy.context.evaluated_depsgraph_get()
    rbvh=BVHTree.FromObject(ro,dg); RM=ro.matrix_world; RI=RM.inverted()
    def rooftop(p):
        o=RI@Vector((p.x,p.y,147.0)); d=(RI.to_3x3()@Vector((0,0,1))).normalized()
        h=rbvh.ray_cast(o,d,10.0)
        if h[0] is None: return TOP
        return max(TOP,(RM@h[0]).z+0.05)
    bm=bmesh.new(); n=0
    for f in me.polygons:
        vs=[M@me.vertices[i].co for i in f.vertices]; cc=sum(vs,Vector())/len(vs)
        zt=max(v.z for v in vs)
        hd={}
        for v in vs:
            k=(round(v.x,3),round(v.y,3)); hd[k]=max(hd.get(k,-1e9),v.z)
        zlo=min(hd.values())  # lowest endpoint top: also catches sloped-top jog faces (e.g. 126: 145.82->149.06)
        if abs(f.normal.z)<0.1 and -24.5<cc.x<-17.5 and 109.5<cc.y<117 and (145.2<zlo<146.0 or 145.2<zt<146.0):
            ks=list(hd)
            if len(ks)<2: continue
            hn=Vector((f.normal.x,f.normal.y)).normalized(); dd=Vector((-hn.y,hn.x))
            ks.sort(key=lambda k: Vector(k).dot(dd))
            a=Vector(ks[0]); b=Vector(ks[-1]); za=hd[ks[0]]; zb=hd[ks[-1]]
            if (b-a).length<0.3: continue
            d=(b-a).normalized(); nrm=Vector((-d.y,d.x)); mid=(a+b)/2
            if (ctr-mid).dot(nrm)<0: nrm=-nrm
            pts=[ks[0],ks[-1]]
            quad=[a,b,b+nrm*0.2,a+nrm*0.2]; zz=[za,zb,zb,za]
            bot=[bm.verts.new((p.x,p.y,zq-0.15)) for p,zq in zip(quad,zz)]; tp=[bm.verts.new((p.x,p.y,rooftop(p))) for p in quad]; print('TOPS',[round(v.co.z,2) for v in tp])
            bm.faces.new(bot[::-1]); bm.faces.new(tp)
            for i in range(4): bm.faces.new((bot[i],bot[(i+1)%4],tp[(i+1)%4],tp[i]))
            n+=1; print("SEG",f.index,pts[0],pts[-1],round(za,2),round(zb,2))
    m2=bpy.data.meshes.new(NAME); bm.normal_update(); bm.to_mesh(m2); bm.free()
    for p in m2.polygons: p.use_smooth=False
    o=bpy.data.objects.new(NAME,m2)
    col=bpy.data.collections.get(COL) or bpy.data.collections.new(COL)
    if COL not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    col.objects.link(o); m2.materials.append(w.material_slots[0].material)
    # same UVs-free material: block base uses object/generated coords? keep as is
    print('INFILL segs',n)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
