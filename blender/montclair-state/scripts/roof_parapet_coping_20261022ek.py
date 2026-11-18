# Session ek (Oct 22 2026 ~12:30 AM ET): metal coping caps on parapet / roof-step top edges of the 7
# "X roof (LiDAR)" meshes whose near-vertical faces were moved to wall material in ej.
# Top edge = edge of a near-vertical face (|nz|<0.35) at that face's max z whose other face points up (nz>0.8).
# Each edge gets a box 0.30 m wide (0.03 m overhang outward past the wall face), from z-0.04 to z+0.05.
# Generic detail: coping profile/colour is typical, NOT measured. Idempotent; SAVE=1 saves; REVERT=1 removes.
import bpy, bmesh, os
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='Roof_coping_caps_ek'
col=bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)
if REVERT:
    print('REVERTED')
else:
    m=bpy.data.materials.get('ek_coping_metal')
    if not m:
        m=bpy.data.materials.new('ek_coping_metal'); m.use_nodes=True
        b=m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value=(0.50,0.50,0.48,1); b.inputs['Metallic'].default_value=0.55
        b.inputs['Roughness'].default_value=0.42
    col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    names=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.endswith('roof (LiDAR)') and 'ej_orig_mi' in o.data.attributes]
    tot=0
    for n in names:
        o=bpy.data.objects[n]; mw=o.matrix_world; n3=mw.to_3x3()
        bm=bmesh.new(); bm.from_mesh(o.data)
        out=bmesh.new(); cnt=0; L=0
        for f in bm.faces:
            fn=(n3@f.normal).normalized()
            if abs(fn.z)>=0.35: continue
            zmax=max((mw@v.co).z for v in f.verts)
            for e in f.edges:
                a=mw@e.verts[0].co; c=mw@e.verts[1].co
                if min(a.z,c.z)<zmax-0.15: continue
                up=[g for g in e.link_faces if g is not f and (n3@g.normal).normalized().z>0.8]
                if not up: continue
                d=Vector((c.x-a.x,c.y-a.y,0)); l=d.length
                if l<0.05: continue
                d.normalize(); p=Vector((-d.y,d.x,0))
                if p.dot(Vector((fn.x,fn.y,0)))<0: p=-p   # p points outward (wall face side)
                a2=a-d*0.03; c2=c+d*0.03
                vs=[]
                for base in (a2,c2):
                    for off in (0.03,-0.27):
                        for dz in (-0.04,0.05):
                            vs.append(out.verts.new(base+p*off+Vector((0,0,dz))))
                # vs index: (end,off,dz) -> end*4+off*2+dz
                F=lambda *ix: out.faces.new([vs[i] for i in ix])
                F(0,1,3,2);F(4,6,7,5);F(1,5,7,3);F(0,2,6,4);F(2,3,7,6);F(0,4,5,1)
                cnt+=1; L+=l
        bm.free()
        bmesh.ops.recalc_face_normals(out, faces=out.faces)
        me=bpy.data.meshes.new('ek_coping_'+n); out.to_mesh(me); out.free(); me.materials.append(m)
        ob=bpy.data.objects.new('ek coping caps '+n.replace(' roof (LiDAR)','')+' (generic, UNVERIFIED profile)', me)
        col.objects.link(ob); tot+=cnt
        print('COPING',n,cnt,'edges',round(L,1),'m')
    print('TOTAL',tot)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
