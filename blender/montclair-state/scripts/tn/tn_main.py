# tn (Nov 4 2026 ~11:35 PM ET, MAIN, day 8 Student Center east edge). ALL UNVERIFIED, reversible (REVERT=1).
# Blanton Hall (OSM 313029108) facade articulation after the 1981 construction photos (refs/blanton/):
# expressed precast vertical piers at every 2nd TI window-bay boundary (6.6 m) and slab-edge spandrel bands under each window row,
# plus a darker concrete-block ground storey band. Geometry only added (collection TN_Blanton_precast_frame_UNVERIFIED); TI masses untouched.
import bpy, bmesh, os, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
CN='TN_Blanton_precast_frame_UNVERIFIED'
def revert():
    for o in [o for o in bpy.data.objects if 'tn_obj' in o]:
        me=o.data; bpy.data.objects.remove(o)
        if me and me.users==0 and hasattr(me,'vertices'): bpy.data.meshes.remove(me)
        elif me and me.users==0: bpy.data.cameras.remove(me)
    c=bpy.data.collections.get(CN)
    if c: bpy.data.collections.remove(c)
    for n in ('TN_precast_pier_UNVERIFIED','TN_spandrel_band_UNVERIFIED','TN_block_base_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    nr=0
    for me in bpy.data.meshes:
        if 'tn_dir_orig' in me.attributes:
            a=me.attributes['tn_dir_orig']; v=[0.0]*(3*len(a.data)); a.data.foreach_get('vector',v)
            me.attributes['ti_dir'].data.foreach_set('vector',v); me.attributes.remove(me.attributes['tn_dir_orig']); nr+=1
    print('TN reverted (dir meshes restored %d)'%nr)
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene
def mat(name,c0,c1,rough,scale,streak):
    m=bpy.data.materials.new(name); m.use_nodes=True; N=m.node_tree.nodes; L=m.node_tree.links; b=N['Principled BSDF']
    tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=scale; nz.inputs['Detail'].default_value=8
    L.new(tc.outputs['Object'],nz.inputs['Vector']); cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=c0; cr.color_ramp.elements[1].color=c1
    L.new(nz.outputs['Fac'],cr.inputs[0]); last=cr.outputs['Color']
    if streak:
        mp=N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1.8,1.8,0.07); L.new(tc.outputs['Object'],mp.inputs['Vector'])
        n2=N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=1.4; n2.inputs['Detail'].default_value=3; L.new(mp.outputs[0],n2.inputs['Vector'])
        r2=N.new('ShaderNodeMapRange'); r2.inputs['From Min'].default_value=0.45; r2.inputs['From Max'].default_value=0.75; r2.inputs['To Min'].default_value=1.0; r2.inputs['To Max'].default_value=0.86
        L.new(n2.outputs['Fac'],r2.inputs['Value'])
        mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
        cv=N.new('ShaderNodeCombineColor'); L.new(r2.outputs[0],cv.inputs[0]); L.new(r2.outputs[0],cv.inputs[1]); L.new(r2.outputs[0],cv.inputs[2])
        L.new(last,mx.inputs['A']); L.new(cv.outputs[0],mx.inputs['B']); last=mx.outputs['Result']
    L.new(last,b.inputs['Base Color']); b.inputs['Roughness'].default_value=rough; b.inputs['Specular IOR Level'].default_value=0.25
    bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.15; L.new(nz.outputs['Fac'],bp.inputs['Height']); L.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
PM=mat('TN_precast_pier_UNVERIFIED',(0.55,0.53,0.49,1),(0.64,0.62,0.57,1),0.85,3.0,True)
BM=mat('TN_spandrel_band_UNVERIFIED',(0.50,0.48,0.44,1),(0.60,0.58,0.53,1),0.88,4.0,True)
KM=mat('TN_block_base_UNVERIFIED',(0.40,0.39,0.36,1),(0.50,0.48,0.45,1),0.92,6.0,False)
col=bpy.data.collections.new(CN); sc.collection.children.link(col); col['tn_obj']=1
bmP=bmesh.new(); bmB=bmesh.new(); bmK=bmesh.new()
def box(bm,c,u,n,hw,d,z0,z1):
    # c on the wall face; u along wall; n outward; hw half-width along u; d depth proud
    pts=[]
    for a,b in ((-hw,-0.02),(hw,-0.02),(hw,d),(-hw,d)):
        p=c+u*a+n*b; pts.append((p.x,p.y))
    vb=[bm.verts.new((x,y,z0)) for x,y in pts]; vt=[bm.verts.new((x,y,z1)) for x,y in pts]
    bm.faces.new(vb[::-1]); bm.faces.new(vt)
    for i in range(4): bm.faces.new((vb[i],vb[(i+1)%4],vt[(i+1)%4],vt[i]))
BAY=3.3; npier=nband=0
objs=[o for o in bpy.data.objects if o.name.startswith('TI_Blanton_Hall_313029108') and o.type=='MESH']
lo=[o for o in objs if '_lower_' in o.name][0]
lo_top=max((lo.matrix_world@v.co).z for v in lo.data.vertices)
for o in objs:
    me=o.data; mw=o.matrix_world; V=me.vertices
    dirs=me.attributes['ti_dir'].data; fl=me.attributes['ti_floor'].data; za=me.attributes['ti_z0'].data; zt=me.attributes['ti_z1'].data
    upper='_upper' in o.name
    for p in me.polygons:
        if abs(p.normal.z)>0.3 or p.material_index!=0: continue
        ws=[mw@V[i].co for i in p.vertices]; zmin=min(w.z for w in ws); zmax=max(w.z for w in ws)
        if zmax-zmin<2.0: continue   # parapet inner faces etc.
        u=Vector(dirs[p.index].vector); u.z=0
        if u.length<0.5: continue
        u.normalize(); n=(mw.to_3x3()@p.normal); n.z=0; n.normalize()
        if abs(u.dot(n))>0.2: continue
        ss=[w.to_2d().dot(u.to_2d()) for w in ws]; s0,s1=min(ss),max(ss)
        if s1-s0<6.0: continue
        cen=mw@p.center; base=cen-u*(cen.to_2d().dot(u.to_2d()))  # point on wall line with s=0
        base.z=0
        F=fl[p.index].value; Z0=za[p.index].value; Z1=zt[p.index].value
        zb=zmin if not upper else max(zmin,lo_top)
        if upper and zmax<=lo_top+0.5: continue
        # outer-face check: skip faces whose normal points into another TI Blanton mass (shared interior walls)
        # piers at every 2nd bay boundary
        k0=math.ceil((s0+0.5)/(2*BAY)); k1=math.floor((s1-0.5)/(2*BAY))
        for k in range(k0,k1+1):
            s=k*2*BAY; c=base+u*s
            box(bmP,c,u,n,0.22,0.24,zb,zmax+0.05); npier+=1
        # end piers (corners) a bit wider
        for s,sg in ((s0,1),(s1,-1)):
            c=base+u*(s+sg*0.35); box(bmP,c,u,n,0.35,0.26,zb,zmax+0.05); npier+=1
        # spandrel bands under each window row (TI window starts at zr=0.95+j*F above Z0, opening 0.46*F)
        L=(s1-s0); cm=base+u*((s0+s1)/2)
        j=0
        while True:
            zw=Z0+0.95+j*F
            if zw>Z1-0.9: break
            if zw-0.32>zb+0.05 and zw<zmax-0.3:
                box(bmB,cm,u,n,L/2-0.02,0.12,zw-0.34,zw-0.04); nband+=1
            j+=1
        # concrete-block ground storey band (lower mass only) up to the first window row
        if not upper:
            box(bmK,cm,u,n,L/2-0.03,0.06,zmin,Z0+0.62)
def emit(bm,name,m):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    for pp in me.polygons: pp.use_smooth=False
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['tn_obj']=1
    o['UNVERIFIED']='Blanton precast frame after 1981 construction photos (Sprague Library Archives); spacing tied to TI window bays; cladding colour not confirmed'
    return o
a=emit(bmP,'TN_Blanton_piers_UNVERIFIED',PM); b=emit(bmB,'TN_Blanton_spandrel_bands_UNVERIFIED',BM); c=emit(bmK,'TN_Blanton_block_base_UNVERIFIED',KM)
print('TN piers',npier,'bands',nband,'polys',len(a.data.polygons),len(b.data.polygons),len(c.data.polygons),'lo_top',round(lo_top,2))
# closeup camera on Blanton's south face
import json
bb=[lo.matrix_world@Vector(v) for v in lo.bound_box]
cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
print('TN Blanton bbox',round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),round(min(v.y for v in bb),1),round(max(v.y for v in bb),1),round(min(v.z for v in bb),1),round(max(v.z for v in bb),1))
# ---- Bohn window phase: the egg-crate shader takes fract(dot(world pos, ti_dir)/bay); OSM walls on different step levels differ by
# a fraction of a degree, which at ~400 m from the origin shifts the window columns by metres. Snap ti_dir to the 70.5 deg building axis.
AX=math.radians(70.5); AXES=[Vector((math.cos(AX+k*math.pi/2),math.sin(AX+k*math.pi/2),0)) for k in range(4)]
nsn=0; nm=0
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith(('TK_Bohn_Hall','TL_Bohn_Hall')): continue
    me=o.data
    if 'ti_dir' not in me.attributes or 'tn_dir_orig' in me.attributes: continue
    a=me.attributes['ti_dir']; v=[0.0]*(3*len(a.data)); a.data.foreach_get('vector',v)
    me.attributes.new('tn_dir_orig','FLOAT_VECTOR','FACE'); me.attributes['tn_dir_orig'].data.foreach_set('vector',v)
    out=list(v)
    for i in range(len(v)//3):
        d=Vector((v[3*i],v[3*i+1],0))
        if d.length<0.5: continue
        d.normalize(); best=max(AXES,key=lambda A:A.dot(d))
        if best.dot(d)>math.cos(math.radians(12)): out[3*i:3*i+3]=[best.x,best.y,0.0]; nsn+=1
    me.attributes['ti_dir'].data.foreach_set('vector',out); nm+=1
print('TN Bohn dir snapped faces',nsn,'meshes',nm)
dg=bpy.context.evaluated_depsgraph_get()
tj=bpy.data.objects.get('TJ_CAM_eye_Webster_lawn_Blanton_from_S')
if tj:
    L0=tj.matrix_world.translation; dv=(tj.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    iw=lo.matrix_world.inverted(); r=lo.ray_cast(iw@L0,(iw.to_3x3()@dv).normalized())
    if r[0]:
        hit=lo.matrix_world@r[1]; nn=(lo.matrix_world.to_3x3()@r[2]); nn.z=0; nn.normalize(); uu=Vector((-nn.y,nn.x,0))
        gz=hit.z
        GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']
        loc=hit+nn*16+uu*9
        for g in GN:
            go=bpy.data.objects.get(g)
            if not go: continue
            e=go.evaluated_get(dg); gw=go.matrix_world.inverted(); rr=e.ray_cast(gw@Vector((loc.x,loc.y,400)),(gw.to_3x3()@Vector((0,0,-1))).normalized())
            if rr[0]: gz=(go.matrix_world@rr[1]).z; break
        loc.z=gz+2.2; tgt=hit+uu*(-4); tgt.z=gz+5.5
        cd=bpy.data.cameras.new('TN_CAM_closeup_Blanton_piers_bands'); cd.lens=30; cd.clip_end=30000
        co=bpy.data.objects.new('TN_CAM_closeup_Blanton_piers_bands',cd); col.objects.link(co); co['tn_obj']=1; co.location=loc
        d=tgt-loc; co.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2)
        print('TN closeup cam',[round(v,1) for v in loc],'hit',[round(v,1) for v in hit])
print('TN objects',len(bpy.data.objects))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
