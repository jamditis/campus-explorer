# qy (Nov 3 2026 ~3:35 AM ET, MAIN, day 7 W lawn plaza). ALL UNVERIFIED, reversible: REVERT=1.
# Plaza rim banding: a 0.30 m smooth-concrete edge band + 0.12 m curb face along the OSM outline edges of the qx
# pedestrian-area paving (313024781, 313027423). Only paving boundary edges within 0.7 m of the OSM outline get a band
# (internal boundaries against existing walks are skipped). Band top = paving + 1.5 cm, curb face drops 0.14 m outside.
# Band outer face sits 2 cm outside the qx edge curtain (never coplanar). Generic finish (no photo of the actual plaza edge).
import bpy, bmesh, os, json, math
from mathutils import Vector
COL='QY_plaza_rim_band_UNVERIFIED'; MN='QY_plaza_rim_band_concrete_UNVERIFIED'
def revert():
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith('QY_rim') and m.users==0]: bpy.data.meshes.remove(me)
    m=bpy.data.materials.get(MN)
    if m and m.users==0: bpy.data.materials.remove(m)
    print('QYR reverted')
revert()
if os.environ.get('REVERT')=='1':
    if os.environ.get('QYSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
D=json.load(open('data/scene_data.json')); F={str(f['id']):f for f in D['features']}
def segd(p,a,b):
    ab=b-a; t=max(0,min(1,(p-a).dot(ab)/max(ab.length_squared,1e-9))); return (p-(a+ab*t)).length
# material
m=bpy.data.materials.new(MN); m.use_nodes=True; N=m.node_tree.nodes; L=m.node_tree.links; N.clear()
out=N.new('ShaderNodeOutputMaterial'); bs=N.new('ShaderNodeBsdfPrincipled'); L.new(bs.outputs[0],out.inputs[0])
tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3.0; nz.inputs['Detail'].default_value=8
L.new(tc.outputs['Object'],nz.inputs['Vector'])
cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.17,0.165,0.155,1); cr.color_ramp.elements[1].color=(0.235,0.23,0.215,1)
L.new(nz.outputs['Fac'],cr.inputs[0]); L.new(cr.outputs[0],bs.inputs['Base Color']); bs.inputs['Roughness'].default_value=0.78
bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.08; L.new(nz.outputs['Fac'],bp.inputs['Height']); L.new(bp.outputs[0],bs.inputs['Normal'])
col=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(col)
OUT=0.02; W=0.30; LIFT=0.015; DROP=0.14; tot=0
for aid in ('313024781','313027423'):
    src=bpy.data.objects['QXP_pedestrian_area_%s_paving_UNVERIFIED'%aid]; mw=src.matrix_world
    pts=[Vector((p[0],p[1],0)) for p in F[aid]['pts']]; segs=list(zip(pts,pts[1:]+pts[:1]))
    def near(v): q=Vector((v.x,v.y,0)); return min(segd(q,a,b) for a,b in segs)<0.7
    bm=bmesh.new(); bm.from_mesh(src.data); bm.faces.ensure_lookup_table()
    top={f for f in bm.faces if f.normal.z>0.5}
    edges=[]
    for e in bm.edges:
        lf=[f for f in e.link_faces if f in top]
        if len(lf)!=1: continue
        a,b=[mw@v.co for v in e.verts]
        if not (near(a) and near(b)): continue
        c=mw@lf[0].calc_center_median(); d=(b-a); d.z=0
        if d.length<1e-4: continue
        n=Vector((-d.y,d.x,0)).normalized()
        if n.dot(c-a)<0: n=-n
        edges.append((e.verts[0].index,e.verts[1].index,a,b,n))
    vn={}; vp={}
    for i,j,a,b,n in edges:
        for k,p in ((i,a),(j,b)): vn[k]=vn.get(k,Vector())+n; vp[k]=p
    ob=bmesh.new(); top_v={}; in_v={}; low_v={}; low_in={}
    for k,p in vp.items():
        n=vn[k]; n.z=0; n=n.normalized() if n.length>1e-6 else n
        top_v[k]=ob.verts.new((p.x-n.x*OUT,p.y-n.y*OUT,p.z+LIFT)); in_v[k]=ob.verts.new((p.x+n.x*W,p.y+n.y*W,p.z+LIFT))
        low_v[k]=ob.verts.new((p.x-n.x*OUT,p.y-n.y*OUT,p.z-DROP)); low_in[k]=ob.verts.new((p.x+n.x*W,p.y+n.y*W,p.z-0.02))
    for i,j,a,b,n in edges:
        for vs in ((top_v[i],top_v[j],in_v[j],in_v[i]),(low_v[i],low_v[j],top_v[j],top_v[i]),(in_v[i],in_v[j],low_in[j],low_in[i])):
            try: ob.faces.new(vs)
            except ValueError: pass
    bmesh.ops.recalc_face_normals(ob,faces=ob.faces)
    me=bpy.data.meshes.new('QY_rim_%s'%aid); ob.to_mesh(me); ob.free(); bm.free()
    for p in me.polygons: p.use_smooth=False
    o=bpy.data.objects.new('QY_plaza_rim_band_%s_UNVERIFIED'%aid,me); col.objects.link(o); me.materials.append(m)
    tot+=len(edges); print('QYR',aid,'edges',len(edges),'faces',len(me.polygons))
print('QYR total edges',tot)
if os.environ.get('QYSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
