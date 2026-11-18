# Session el (Oct 22 2026 ~1:40 AM ET): the 155 plain dark Roof_vent boxes become generic mushroom exhaust fans:
# the box is lowered to a curb (top at 55% of its height; original z kept in point attr el_orig_z), and a galvanised
# neck (r 0.30 s, 55-72% H, dark louvre band) + hood (r 0.47 s, 72% H to top+0.06 m, domed lid) is added on top.
# Positions/sizes from the existing boxes; the fan type is TYPICAL, NOT photo-checked. SAVE=1; REVERT=1 restores.
import bpy, bmesh, os, math
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='Roof_vent_hoods_el'
col=bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)
o=bpy.data.objects['Roof_vent']; me=o.data; mw=o.matrix_world; inv=mw.inverted()
at=me.attributes.get('el_orig_z')
if at:
    for i,v in enumerate(me.vertices): v.co.z=at.data[i].value
    me.attributes.remove(at)
if REVERT:
    print('REVERTED')
else:
    at=me.attributes.new('el_orig_z','FLOAT','POINT')
    for i,v in enumerate(me.vertices): at.data[i].value=v.co.z
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    seen=set(); isl=[]
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; cur=[]
        while st:
            x=st.pop()
            if x.index in seen: continue
            seen.add(x.index); cur.append(x.index); st.extend(e.other_vert(x) for e in x.link_edges)
        isl.append(cur)
    bm.free()
    galv=bpy.data.materials['ek_coping_metal']; dark=bpy.data.materials['Roof_vent_dark_metal']
    out=bmesh.new(); n=0
    def cyl(cx,cy,z0,z1,r,mi,seg=16,dome=0.0):
        ring0=[out.verts.new((cx+r*math.cos(2*math.pi*k/seg),cy+r*math.sin(2*math.pi*k/seg),z0)) for k in range(seg)]
        ring1=[out.verts.new((cx+r*math.cos(2*math.pi*k/seg),cy+r*math.sin(2*math.pi*k/seg),z1)) for k in range(seg)]
        for k in range(seg):
            f=out.faces.new((ring0[k],ring0[(k+1)%seg],ring1[(k+1)%seg],ring1[k])); f.material_index=mi; f.smooth=True
        f=out.faces.new(list(reversed(ring0))); f.material_index=mi
        if dome>0:
            top=out.verts.new((cx,cy,z1+dome))
            for k in range(seg):
                f=out.faces.new((ring1[k],ring1[(k+1)%seg],top)); f.material_index=mi; f.smooth=True
        else:
            f=out.faces.new(ring1); f.material_index=mi
    for ids in isl:
        W=[mw@me.vertices[i].co for i in ids]
        xs=[p.x for p in W]; ys=[p.y for p in W]; zs=[p.z for p in W]
        sx=max(xs)-min(xs); sy=max(ys)-min(ys); H=max(zs)-min(zs)
        if min(sx,sy)<0.2 or H<0.2: continue
        s=min(sx,sy); z0=min(zs); z1=max(zs); cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2
        zc=z0+0.55*H
        for i in ids:
            p=mw@me.vertices[i].co
            if p.z>z0+0.5*H: me.vertices[i].co=inv@Vector((p.x,p.y,zc))
        cyl(cx,cy,zc,z0+0.62*H,0.30*s,0)
        cyl(cx,cy,z0+0.62*H,z0+0.72*H,0.28*s,1)
        cyl(cx,cy,z0+0.72*H,z1+0.02,0.47*s,0,20,dome=0.04+0.06*s)
        n+=1
    hm=bpy.data.meshes.new('el_vent_hoods'); out.to_mesh(hm); out.free(); hm.materials.append(galv); hm.materials.append(dark)
    col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    ob=bpy.data.objects.new('el roof exhaust fan hoods (generic, UNVERIFIED type)',hm); col.objects.link(ob)
    me.update(); print('HOODS',n,'of',len(isl),'islands')
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
