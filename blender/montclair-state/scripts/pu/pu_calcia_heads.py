# pu: Calcia slot heads that run into the low LiDAR wall top (e.g. the west-wing roof step at x~-82,y~164): ps cut the
# opening up to the shell top, pt's top infill starts above the old top edge, so the reveal's top face showed from above as
# a small dark notch. For each PR slot head bar with no wall/infill 12 cm above it (BVH gap test), add a brick quad 1 cm
# behind the wall face from the head up to the roof underside 147.42 m (PU_Calcia_slot_head_infill_UNVERIFIED, same
# object-linked brick as PT infill, win_top 0 -> no shader windows). REVERT=1 removes the object.
import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; ON='PU_Calcia_slot_head_infill_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me); print('REVERTED_PU_HEADS')
if not REV:
    def wbm(names):
        b=bmesh.new()
        for n in names:
            ob=bpy.data.objects[n]; t=bmesh.new(); t.from_mesh(ob.data); t.transform(ob.matrix_world)
            tm=bpy.data.meshes.new('_t'); t.to_mesh(tm); t.free(); b.from_mesh(tm); bpy.data.meshes.remove(tm)
        return b
    bw=wbm(['Calcia Hall walls','PT_Calcia_wall_top_infill_UNVERIFIED']); bw.faces.ensure_lookup_table()
    bvh=BVHTree.FromBMesh(bw)
    pr=bpy.data.objects['PR_Calcia_slot_surrounds_UNVERIFIED']; bp=bmesh.new(); bp.from_mesh(pr.data); bp.transform(pr.matrix_world)
    bars=[]; seen=set()
    for v0 in bp.verts:
        if v0.index in seen: continue
        isl=[]; st=[v0]; seen.add(v0.index)
        while st:
            v=st.pop(); isl.append(v.co.copy())
            for e in v.link_edges:
                u=e.other_vert(v)
                if u.index not in seen: seen.add(u.index); st.append(u)
        zs=[c.z for c in isl]; c=sum(isl,Vector())/len(isl)
        hl=max((a-b).xy.length for a in isl for b in isl)
        if max(zs)-min(zs)<0.1 and 0.85<hl<1.0: bars.append((c,max(zs)))
    # top bar of each slot = highest bar within 0.4 m horizontally
    tops=[b for b in bars if not any((o[0].xy-b[0].xy).length<0.4 and o[0].z>b[0].z+0.3 for o in bars)]
    bm=bmesh.new(); uvl=bm.loops.layers.uv.new('facade'); n=0
    for c,zt in tops:
        test=c+Vector((0,0,0.14))
        loc,nor,fi,d=bvh.find_nearest(test)
        if fi is not None and d<0.06: continue
        loc,nor,fi,d=bvh.find_nearest(c)
        if fi is None or d>0.4: continue
        f=bw.faces[fi]; nn=f.normal.copy(); nn.z=0; nn.normalize()
        t=Vector((-nn.y,nn.x,0)); pp=loc-(loc-f.verts[0].co).dot(nn)*nn*0   # point on wall plane
        # project bar centre onto the wall plane, then 1 cm behind it (whichever side the bar is on = outside)
        side=1 if (c-loc).dot(nn)>0 else -1; base=c-nn*((c-loc).dot(nn)) - nn*side*0.01
        z0=zt-0.03; z1=147.42
        if z1-z0<0.05: continue
        q=[base+t*-0.6+Vector((0,0,z0-base.z)),base+t*0.6+Vector((0,0,z0-base.z)),base+t*0.6+Vector((0,0,z1-base.z)),base+t*-0.6+Vector((0,0,z1-base.z))]
        vs=[bm.verts.new(p) for p in q]
        if side<0: vs.reverse()
        fc=bm.faces.new(vs)
        for l in fc.loops: l[uvl].uv=(l.vert.co.dot(t), l.vert.co.z-137.0)
        n+=1
    print('PU_HEADS bars',len(bars),'tops',len(tops),'patched',n)
    me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free(); bw.free(); bp.free()
    src=bpy.data.objects['PT_Calcia_wall_top_infill_UNVERIFIED']
    for m in src.data.materials: me.materials.append(m)
    o=bpy.data.objects.new(ON,me)
    for k in src.keys():
        if not k.startswith('_'): o[k]=src[k]
    o['win_top']=0.0; o['source_note']='UNVERIFIED pu head infill'
    src.users_collection[0].objects.link(o)
    for i,s in enumerate(src.material_slots):
        o.material_slots[i].link=s.link
        if s.link=='OBJECT': o.material_slots[i].material=s.material
    print('PU_HEADS obj',ON,'slots',[(s.link,s.material.name if s.material else None) for s in o.material_slots])
