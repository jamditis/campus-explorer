# ti (Nov 4 2026 ~6:25 PM ET, MAIN, day 8 Student Center east edge). ALL UNVERIFIED, reversible (REVERT=1).
# Stone Hall (OSM 313028565) + Blanton Hall (OSM 313029108) as LiDAR-height massings: OSM footprint, roof levels split from the 2017 1 m DSM
# (data/ti/east_levels.json), 0.5 m parapets, procedural punched-window walls (bay/floor spacing typical, NO facade refs), grey membrane roofs.
# Culls grass points inside the footprints. Adds TI cameras.
import bpy, bmesh, os, json, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
def revert():
    for o in [o for o in bpy.data.objects if 'ti_obj' in o]:
        me=o.data; bpy.data.objects.remove(o)
        if me and me.users==0 and hasattr(me,'vertices'): bpy.data.meshes.remove(me)
        elif me and me.users==0: bpy.data.cameras.remove(me)
    for o in bpy.data.objects:
        if 'ti_orig_mesh' in o:
            cur=o.data; o.data=bpy.data.meshes[o['ti_orig_mesh']]; del o['ti_orig_mesh']; del o['ti_culled']
            if cur.users==0: bpy.data.meshes.remove(cur)
    for n in ('TI_dorm_wall_windows_UNVERIFIED','TI_roof_membrane_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    print('TI reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
def ccw(p):
    a=sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
    return p if a>0 else p[::-1]
# ---- materials
def wallmat():
    m=bpy.data.materials.new('TI_dorm_wall_windows_UNVERIFIED'); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links; b=N['Principled BSDF']
    tc=N.new('ShaderNodeTexCoord'); ge=N.new('ShaderNodeNewGeometry')
    ad=N.new('ShaderNodeAttribute'); ad.attribute_name='ti_dir'; af=N.new('ShaderNodeAttribute'); af.attribute_name='ti_floor'
    a0=N.new('ShaderNodeAttribute'); a0.attribute_name='ti_z0'; a1=N.new('ShaderNodeAttribute'); a1.attribute_name='ti_z1'
    sep=N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'],sep.inputs[0])
    def M(op,a,bv=None,c=None):
        n=N.new('ShaderNodeMath'); n.operation=op
        for i,v in enumerate((a,bv,c)):
            if v is None: continue
            if isinstance(v,(int,float)): n.inputs[i].default_value=v
            else: L.new(v,n.inputs[i])
        return n.outputs[0]
    dp=N.new('ShaderNodeVectorMath'); dp.operation='DOT_PRODUCT'; L.new(tc.outputs['Object'],dp.inputs[0]); L.new(ad.outputs['Vector'],dp.inputs[1])
    fu=M('FRACT',M('DIVIDE',dp.outputs['Value'],3.3))
    zr=M('SUBTRACT',sep.outputs['Z'],a0.outputs['Fac'])
    fz=M('FRACT',M('DIVIDE',M('SUBTRACT',zr,0.95),af.outputs['Fac']))
    inb=M('MULTIPLY',M('GREATER_THAN',zr,0.95),M('LESS_THAN',sep.outputs['Z'],M('SUBTRACT',a1.outputs['Fac'],0.9)))
    sn=N.new('ShaderNodeSeparateXYZ'); L.new(ge.outputs['True Normal'],sn.inputs[0]); wall=M('LESS_THAN',M('ABSOLUTE',sn.outputs['Z']),0.5)
    ok=M('MULTIPLY',inb,wall)
    # opening (frame outer) 0.30..0.70 of the 3.3 m bay (1.32 m wide), 0..0.46 of the storey; glass inset by ~6 cm; centre mullion
    fr=M('MULTIPLY',M('MULTIPLY',M('GREATER_THAN',fu,0.30),M('LESS_THAN',fu,0.70)),M('LESS_THAN',fz,0.46))
    gl=M('MULTIPLY',M('MULTIPLY',M('GREATER_THAN',fu,0.318),M('LESS_THAN',fu,0.682)),M('MULTIPLY',M('GREATER_THAN',fz,0.02),M('LESS_THAN',fz,0.44)))
    gl=M('MULTIPLY',gl,M('GREATER_THAN',M('ABSOLUTE',M('SUBTRACT',fu,0.5)),0.006))
    sill=M('MULTIPLY',M('MULTIPLY',M('GREATER_THAN',fu,0.29),M('LESS_THAN',fu,0.71)),M('GREATER_THAN',fz,0.975))
    frm=M('MULTIPLY',fr,ok); win=M('MULTIPLY',gl,ok); sil=M('MULTIPLY',sill,ok)
    nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.6; nz.inputs['Detail'].default_value=6; L.new(tc.outputs['Object'],nz.inputs['Vector'])
    cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.46,0.44,0.40,1); cr.color_ramp.elements[1].color=(0.58,0.56,0.52,1); L.new(nz.outputs['Fac'],cr.inputs[0])
    # vertical run-off grime: noise stretched in z, stronger near the top
    vs=N.new('ShaderNodeMapping'); vs.inputs['Scale'].default_value=(1.6,1.6,0.08); L.new(tc.outputs['Object'],vs.inputs['Vector'])
    nz2=N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value=1.5; nz2.inputs['Detail'].default_value=3; L.new(vs.outputs[0],nz2.inputs['Vector'])
    gr=M('MULTIPLY',M('MULTIPLY',M('SUBTRACT',nz2.outputs['Fac'],0.5),2.2),wall)
    grc=M('MAXIMUM',gr,0.0)
    mxg=N.new('ShaderNodeMix'); mxg.data_type='RGBA'; mxg.blend_type='MULTIPLY'; mxg.inputs['B'].default_value=(0.72,0.70,0.66,1)
    L.new(grc,mxg.inputs['Factor']); L.new(cr.outputs['Color'],mxg.inputs['A'])
    fb=M('LESS_THAN',M('FRACT',M('DIVIDE',zr,af.outputs['Fac'])),0.05)
    mxb=N.new('ShaderNodeMix'); mxb.data_type='RGBA'; mxb.blend_type='MULTIPLY'; mxb.inputs['B'].default_value=(0.88,0.87,0.85,1)
    L.new(M('MULTIPLY',fb,M('MULTIPLY',wall,M('GREATER_THAN',zr,0.5))),mxb.inputs['Factor']); L.new(mxg.outputs['Result'],mxb.inputs['A'])
    ms=N.new('ShaderNodeMix'); ms.data_type='RGBA'; ms.inputs['B'].default_value=(0.66,0.64,0.60,1); L.new(sil,ms.inputs['Factor']); L.new(mxb.outputs['Result'],ms.inputs['A'])
    mf=N.new('ShaderNodeMix'); mf.data_type='RGBA'; mf.inputs['B'].default_value=(0.16,0.15,0.14,1); L.new(frm,mf.inputs['Factor']); L.new(ms.outputs['Result'],mf.inputs['A'])
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.inputs['B'].default_value=(0.05,0.06,0.07,1)
    L.new(win,mx.inputs['Factor']); L.new(mf.outputs['Result'],mx.inputs['A']); L.new(mx.outputs['Result'],b.inputs['Base Color'])
    rf=N.new('ShaderNodeMix'); rf.data_type='FLOAT'; rf.inputs['A'].default_value=0.88; rf.inputs['B'].default_value=0.06; L.new(win,rf.inputs['Factor']); L.new(rf.outputs['Result'],b.inputs['Roughness'])
    sp=N.new('ShaderNodeMix'); sp.data_type='FLOAT'; sp.inputs['A'].default_value=0.25; sp.inputs['B'].default_value=1.0; L.new(win,sp.inputs['Factor']); L.new(sp.outputs['Result'],b.inputs['Specular IOR Level'])
    # fake recess: bump down inside the frame
    bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.6; bp.inputs['Distance'].default_value=0.08; L.new(M('SUBTRACT',1.0,frm),bp.inputs['Height']); L.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
def roofmat():
    m=bpy.data.materials.new('TI_roof_membrane_UNVERIFIED'); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links; b=N['Principled BSDF']
    tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.25; nz.inputs['Detail'].default_value=8
    L.new(tc.outputs['Object'],nz.inputs['Vector']); cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.36,0.36,0.35,1); cr.color_ramp.elements[1].color=(0.52,0.52,0.50,1)
    L.new(nz.outputs['Fac'],cr.inputs[0]); L.new(cr.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.9; b.inputs['Specular IOR Level'].default_value=0.2
    return m
WM=wallmat(); RM=roofmat()
col=bpy.data.collections.get('TI_east_dorms_UNVERIFIED') or bpy.data.collections.new('TI_east_dorms_UNVERIFIED')
if col.name not in sc.collection.children: sc.collection.children.link(col)
col['ti_obj']=1
def mass(name,poly,z0,z1,floor,note):
    poly=ccw([tuple(p) for p in poly]); bm=bmesh.new()
    vs=[bm.verts.new((x,y,z0)) for x,y in poly]; f=bm.faces.new(vs)
    r=bmesh.ops.extrude_face_region(bm,geom=[f]); top=[g for g in r['geom'] if isinstance(g,bmesh.types.BMFace)][0]
    for v in top.verts: v.co.z=z1
    bmesh.ops.reverse_faces(bm,faces=[f])
    ins=bmesh.ops.inset_region(bm,faces=[top],thickness=0.3,depth=0)
    for v in top.verts: v.co.z=z1-0.5
    bm.normal_update()
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(WM); me.materials.append(RM)
    ad=me.attributes.new('ti_dir','FLOAT_VECTOR','FACE'); af=me.attributes.new('ti_floor','FLOAT','FACE')
    a0=me.attributes.new('ti_z0','FLOAT','FACE'); a1=me.attributes.new('ti_z1','FLOAT','FACE')
    ad,af,a0,a1=[me.attributes[k] for k in ('ti_dir','ti_floor','ti_z0','ti_z1')]
    V=me.vertices; DIRS=[]; MI=[]
    for p in me.polygons:
        best=(0,(1,0))
        for i in range(len(p.vertices)):
            a=V[p.vertices[i]].co; c=V[p.vertices[(i+1)%len(p.vertices)]].co; dx,dy=c.x-a.x,c.y-a.y; l=math.hypot(dx,dy)
            if l>best[0]: best=(l,(dx/l,dy/l))
        DIRS.extend((best[1][0],best[1][1],0)); MI.append(1 if (p.normal.z>0.9 and p.center.z<z1-0.3) else 0)
    n=len(me.polygons)
    me.attributes['ti_dir'].data.foreach_set('vector',DIRS); me.attributes['ti_floor'].data.foreach_set('value',[floor]*n)
    me.attributes['ti_z0'].data.foreach_set('value',[z0g]*n); me.attributes['ti_z1'].data.foreach_set('value',[z1]*n)
    me.polygons.foreach_set('material_index',MI)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['ti_obj']=1; o['UNVERIFIED']=note
    return o
E=json.load(open('data/ti/east_levels.json'))
SPEC={'313028565':dict(nm='Stone',floor=3.2),'313029108':dict(nm='Blanton',floor=3.0)}
made=[]
for wid,s in SPEC.items():
    e=E[wid]; out=e['outer']
    zs=[gz(x,y) for x,y in out]; zs=[z for z in zs if z is not None]
    zs.sort(); z0g=zs[len(zs)//2] if zs else e['ground_med']; zb=(zs[0] if zs else e['ground_min'])-0.4
    print('TI',e['name'],'ground boundary min/max',round(min(zs),2),round(max(zs),2),'lo',e['lo_top'],'hi',e['hi_top'])
    note='OSM %s footprint (ODbL) + 2017 NJ LiDAR DSM roof levels; walls/windows/parapet typical, NO facade refs'%wid
    made.append(mass('TI_%s_Hall_%s_lower_UNVERIFIED'%(s['nm'],wid),out,zb,e['lo_top'],s['floor'],note))
    for i,hp in enumerate(e['hi_polys']):
        made.append(mass('TI_%s_Hall_%s_upper%d_UNVERIFIED'%(s['nm'],wid,i),hp,e['lo_top']-0.6,e['hi_top'],s['floor'],note))
# overlap check
for wid in SPEC:
    out=E[wid]['outer']; xs=[p[0] for p in out]; ys=[p[1] for p in out]
    for o in bpy.data.objects:
        if o.type!='MESH' or 'ti_obj' in o or o.hide_render: continue
        n=o.name.lower()
        if any(k in n for k in ('terrain','skirt','grass','ground','context','sky','bd_')): continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; bx=[v.x for v in bb]; by=[v.y for v in bb]
        if max(bx)-min(bx)>400: continue
        if min(bx)<max(xs) and max(bx)>min(xs) and min(by)<max(ys) and max(by)>min(ys): print('TI overlap',wid,o.name,round(min(bx)),round(max(bx)),round(min(by)),round(max(by)))
# grass cull (footprint +0.8 m)
import itertools
polys=[E[w]['outer'] for w in SPEC]
bbs=[(min(p[0] for p in P)-1,max(p[0] for p in P)+1,min(p[1] for p in P)-1,max(p[1] for p in P)+1) for P in polys]
from mathutils.geometry import intersect_point_line
def near_edge(x,y,P,d):
    for i in range(len(P)):
        a=Vector((P[i][0],P[i][1],0)); b=Vector((P[(i+1)%len(P)][0],P[(i+1)%len(P)][1],0)); q=Vector((x,y,0))
        t=max(0,min(1,(q-a).dot(b-a)/max((b-a).length_squared,1e-9))); 
        if (a+(b-a)*t-q).length<d: return True
    return False
tot=0
for o in bpy.data.objects:
    if o.type!='MESH' or 'grass' not in o.name.lower() or not o.data.vertices or len(o.data.polygons)>0: continue
    mw=o.matrix_world; idx=[]
    for v in o.data.vertices:
        w=mw@v.co
        for P,(x0,x1,y0,y1) in zip(polys,bbs):
            if x0<w.x<x1 and y0<w.y<y1 and (pip(w.x,w.y,P) or near_edge(w.x,w.y,P,0.8)): idx.append(v.index); break
    if not idx: continue
    me=o.data; o['ti_orig_mesh']=me.name; me.use_fake_user=True; nm=me.copy(); nm.name=me.name+'.ti'; o.data=nm; o['ti_culled']=len(idx)
    bm=bmesh.new(); bm.from_mesh(nm); bm.verts.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.verts[i] for i in idx],context='VERTS'); bm.to_mesh(nm); bm.free()
    tot+=len(idx); print('TI grass culled',o.name,len(idx),'left',len(nm.vertices))
print('TI grass total',tot)
# cameras
def cam(name,loc,tgt,lens):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000; o=bpy.data.objects.new(name,cd); col.objects.link(o); o['ti_obj']=1
    o.location=loc; d=Vector(tgt)-Vector(loc)
    o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2); return o
g=gz(60,250) or 138
cam('TI_CAM_oblique_east_dorms_from_SW',(-20,180,g+75),(150,360,g+5),28)
g2=gz(118,300) or 138
g3=gz(156,328) or 137
cam('TI_CAM_eye_Stone_from_N',(156,328,g3+1.65),(150,268,g3+4),26)
cam('TI_CAM_closeup_Stone_parapet_windows',(124,236,g2+6),(138,252,g2+4),35)
for o in bpy.data.objects:
    if o.type=='CAMERA' and o.name.startswith(('SG_','SF_','SE_')): print('CAM',o.name,[round(v,1) for v in o.location])
print('TI applied',len(made),'masses; objects',len(bpy.data.objects))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
