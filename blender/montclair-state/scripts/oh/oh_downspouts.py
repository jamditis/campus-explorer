# oh: red-brown round downspouts at the convex outer corners of 'Schmitt Hall walls' (photo schmitt_02 shows red-brown
# downspouts at pavilion corners; corner positions on this block UNVERIFIED). Eave soffit ~147.93. REVERT=1 removes.
import bpy, bmesh, os, sys, math
from mathutils import Vector
NAME='OH_Schmitt_downspouts_UNVERIFIED'
REV=os.environ.get('REVERT')=='1'
o=bpy.data.objects.get(NAME)
if o: me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
if not REV:
    w=bpy.data.objects['Schmitt Hall walls']; M=w.matrix_world
    bm=bmesh.new(); bm.from_mesh(w.data); bm.transform(M)
    zt=max(v.co.z for v in bm.verts)
    top=[v for v in bm.verts if v.co.z>zt-0.05]
    # top ring edges -> ordered corners
    ring=[e for e in bm.edges if all(v.co.z>zt-0.05 for v in e.verts)]
    adj={}
    for e in ring:
        a,b=e.verts; adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
    pts=[]
    for v,nb in adj.items():
        if len(nb)!=2: continue
        d1=(nb[0].co-v.co).xy; d2=(nb[1].co-v.co).xy
        if d1.length<1.0 or d2.length<1.0: continue
        ang=math.degrees(d1.angle(d2))
        if ang>150: continue
        pts.append((v.co.copy(),d1.normalized(),d2.normalized()))
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    out=bmesh.new(); n=0; seen=[]
    for p,d1,d2 in pts:
        bis=-(d1+d2).normalized()   # points away from both walls
        q=p.xy+bis*0.16
        # convex test: point outward must be outside the footprint -> ray down from above hits terrain not roof
        h=sc.ray_cast(dg,Vector((q.x,q.y,zt-0.6)),Vector((0,0,-1)))
        if not h[0] or 'Schmitt' in h[4].name or 'OG_' in h[4].name: continue
        if any((q-s).length<3 for s in seen): continue
        seen.append(q); zg=h[1].z
        if h[4].name.startswith('OH_'): pass
        c=bmesh.ops.create_cone(out,cap_ends=True,segments=12,radius1=0.055,radius2=0.055,depth=(147.95-zg))
        for v in c['verts']: v.co+=Vector((q.x,q.y,(147.95+zg)/2))
        # shoe at the foot
        s=bmesh.ops.create_cube(out,size=1.0)
        for v in s['verts']: v.co=Vector((v.co.x*0.14+q.x+bis.x*0.07,v.co.y*0.14+q.y+bis.y*0.07,v.co.z*0.12+zg+0.10))
        n+=1
    me=bpy.data.meshes.new(NAME); out.to_mesh(me)
    o=bpy.data.objects.new(NAME,me); bpy.data.collections['OH_Schmitt_cams_20261031oh'].objects.link(o)
    me.materials.append(bpy.data.materials['OH_Schmitt_win_frame_red_brown'])
    for f in me.polygons: f.use_smooth=True
    print('downspouts',n,'corners',len(pts),'zt',round(zt,2))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
