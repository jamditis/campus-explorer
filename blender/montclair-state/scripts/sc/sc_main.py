# sc (Nov 4 2026 ~12:30 PM ET, MAIN, day 8 Student Center): qt joint/soil-edge method applied to the 7 SB walks (University Promenade + Annex-west).
# Adapted from scripts/qt/qt_main.py. ALL UNVERIFIED, reversible: REVERT=1 -> pre-sc. u is NORMALISED (1 = walk edge); pedestrian walks get
# their own material with a centre longitudinal joint and 2.5 m transverse panels.
# (1) QS footway ribbons get UV 'sc_sl' (u = across m from OSM centreline, v = along m) and a copied material
#     QT_walk_concrete_joints_UNVERIFIED: tooled transverse joints @1.5 m, wider expansion joint @6 m, tooled edge
#     line 5 cm in, edge grime band; bump from the joint mask. Original material untouched (Footpaths_OSM keeps it).
# (2) QT_Richardson_walk_soil_edge_UNVERIFIED: 0.2 m worn-soil strip along both outer edges of each QS footway,
#     1.2 cm over the ground, ragged noise alpha into the lawn.
# (3) camera QT_CAM_closeup_richardson_walk_joints.
import bpy,bmesh,json,math,os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
MATN='SC_walk_concrete_joints_UNVERIFIED'; MATP='SC_promenade_concrete_joints_UNVERIFIED'; SOILM='SC_walk_soil_edge_UNVERIFIED'; COL='SC_AnnexWest_walk_soil_edge_UNVERIFIED'
def revert():
    m0=bpy.data.materials.get('OV_Paving_concrete_walk_tone_UNVERIFIED')
    for o in bpy.data.objects:
        if o.type=='MESH' and o.name.startswith('SB_') and o.name.endswith('_UNVERIFIED') and ('_footway_' in o.name or '_pedestrian_' in o.name):
            for s in o.material_slots:
                if s.material and s.material.name in (MATN,MATP): s.material=m0
            u=o.data.uv_layers.get('sc_sl')
            if u: o.data.uv_layers.remove(u)
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for o in [o for o in bpy.data.objects if o.name.startswith('SC_CAM')]: bpy.data.objects.remove(o,do_unlink=True)
    for me in [m for m in bpy.data.meshes if m.name.startswith('SC_') and m.users==0]: bpy.data.meshes.remove(me)
    for c in [c for c in bpy.data.cameras if c.name.startswith('SC_CAM') and c.users==0]: bpy.data.cameras.remove(c)
    for n in (MATN,MATP,SOILM):
        m=bpy.data.materials.get(n)
        if m and m.users==0: bpy.data.materials.remove(m)
    print('SC reverted')
revert()
if REV:
    if os.environ.get('SCSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
D=json.load(open('data/scene_data.json')); F={str(f['id']):f for f in D['features']}
GN=['Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km','QM_terrain_band_underlay_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
def proj(poly,x,y):
    best=(1e9,0,0); acc=0
    for (ax,ay),(bx,by) in zip(poly[:-1],poly[1:]):
        dx,dy=bx-ax,by-ay; L=math.hypot(dx,dy) or 1e-9
        t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(L*L))); px,py=ax+dx*t,ay+dy*t; d=math.hypot(x-px,y-py)
        if d<best[0]:
            s=((x-ax)*(-dy)+(y-ay)*dx)/L
            best=(d,s,acc+t*L)
        acc+=L
    return best[1],best[2]
# ---- material
m0=bpy.data.materials['OV_Paving_concrete_walk_tone_UNVERIFIED']
def mkmat(NAME,PITCH,CENTRE):
 m=m0.copy(); m.name=NAME; nt=m.node_tree; N=nt.nodes; Lk=nt.links
 P=N['Principled BSDF']; tone=N['OV_walk_tone']; nm=N['Normal Map']
 uvn=N.new('ShaderNodeUVMap'); uvn.uv_map='sc_sl'; uvn.name='SC_uv'; sep=N.new('ShaderNodeSeparateXYZ'); sep.name='SC_sep'; Lk.new(uvn.outputs[0],sep.inputs[0])
 def M(op,a,b=None,nm=None):
     n=N.new('ShaderNodeMath'); n.operation=op; n.name='SC_'+(nm or op)
     for i,v in enumerate((a,b)):
         if v is None: continue
         if isinstance(v,(int,float)): n.inputs[i].default_value=v
         else: Lk.new(v,n.inputs[i])
     return n.outputs[0]
 def dist_line(val,pitch):  # metres from nearest line at multiples of pitch
     f=M('FRACT',M('ADD',M('DIVIDE',val,pitch),0.5)); return M('MULTIPLY',M('ABSOLUTE',M('SUBTRACT',f,0.5)),pitch)
 def band(d,a,b):  # 1 when d<a, 0 when d>b
     n=N.new('ShaderNodeMapRange'); n.name='SC_band'; n.interpolation_type='SMOOTHSTEP'; Lk.new(d,n.inputs[0]); n.inputs[1].default_value=a; n.inputs[2].default_value=b; n.inputs[3].default_value=1; n.inputs[4].default_value=0; return n.outputs[0]
 v=sep.outputs['Y']; u=sep.outputs['X']
 j15=band(dist_line(v,PITCH),0.003,0.008); j6=band(dist_line(v,6.0),0.007,0.013)
 au=M('ABSOLUTE',u); edge_tool=band(M('ABSOLUTE',M('SUBTRACT',au,0.95)),0.003,0.007)
 joint=M('MINIMUM',M('MAXIMUM',M('MAXIMUM',j15,j6),edge_tool),1.0,'joint')
 if CENTRE: joint=M('MAXIMUM',joint,band(au,0.0015,0.0035),'centre')
 # edge grime: |u| 0.75..1.0 -> 0..1, broken by noise
 tc=N.new('ShaderNodeTexCoord'); tc.name='SC_tc'; nz=N.new('ShaderNodeTexNoise'); nz.name='SC_noise'; nz.inputs['Scale'].default_value=1.6; nz.inputs['Detail'].default_value=6; Lk.new(tc.outputs['Object'],nz.inputs['Vector'])
 mr=N.new('ShaderNodeMapRange'); mr.name='SC_edge'; mr.interpolation_type='SMOOTHSTEP'; Lk.new(au,mr.inputs[0]); mr.inputs[1].default_value=0.72; mr.inputs[2].default_value=1.0
 grime=M('MULTIPLY',mr.outputs[0],M('ADD',M('MULTIPLY',nz.outputs['Fac'],0.9),0.15),'grime')
 c1=N.new('ShaderNodeMix'); c1.data_type='RGBA'; c1.blend_type='MIX'; c1.name='SC_grime_mix'
 Lk.new(tone.outputs['Result'],c1.inputs[6]); c1.inputs[7].default_value=(0.20,0.17,0.12,1); Lk.new(M('MULTIPLY',grime,0.45),c1.inputs[0])
 c2=N.new('ShaderNodeMix'); c2.data_type='RGBA'; c2.blend_type='MULTIPLY'; c2.name='SC_joint_mix'
 Lk.new(c1.outputs[2],c2.inputs[6]); c2.inputs[7].default_value=(0.42,0.40,0.37,1); Lk.new(joint,c2.inputs[0])
 Lk.new(c2.outputs[2],P.inputs['Base Color'])
 bp=N.new('ShaderNodeBump'); bp.name='SC_bump'; bp.invert=True; bp.inputs['Strength'].default_value=0.6; bp.inputs['Distance'].default_value=0.006
 Lk.new(joint,bp.inputs['Height']); Lk.new(nm.outputs['Normal'],bp.inputs['Normal']); Lk.new(bp.outputs['Normal'],P.inputs['Normal'])
 return m
m=mkmat(MATN,1.5,False); mp=mkmat(MATP,2.5,True)
# ---- soil material
sm=bpy.data.materials.new(SOILM); sm.use_nodes=True; st=sm.node_tree; S=st.nodes; SL=st.links
sp=S['Principled BSDF']; sp.inputs['Base Color'].default_value=(0.16,0.12,0.08,1); sp.inputs['Roughness'].default_value=0.95
stc=S.new('ShaderNodeTexCoord'); sn=S.new('ShaderNodeTexNoise'); sn.inputs['Scale'].default_value=9; sn.inputs['Detail'].default_value=8; SL.new(stc.outputs['Object'],sn.inputs['Vector'])
suv=S.new('ShaderNodeUVMap'); suv.uv_map='sc_soil'; ss=S.new('ShaderNodeSeparateXYZ'); SL.new(suv.outputs[0],ss.inputs[0])
# alpha = 1 - smoothstep(across 0..1 + (noise-0.5)*0.9, 0.35, 0.75)
ad=S.new('ShaderNodeMath'); ad.operation='MULTIPLY_ADD'; SL.new(sn.outputs['Fac'],ad.inputs[0]); ad.inputs[1].default_value=0.9; ad.inputs[2].default_value=-0.45
a2=S.new('ShaderNodeMath'); a2.operation='ADD'; SL.new(ss.outputs['X'],a2.inputs[0]); SL.new(ad.outputs[0],a2.inputs[1])
smr=S.new('ShaderNodeMapRange'); smr.interpolation_type='SMOOTHSTEP'; SL.new(a2.outputs[0],smr.inputs[0]); smr.inputs[1].default_value=0.35; smr.inputs[2].default_value=0.8; smr.inputs[3].default_value=1; smr.inputs[4].default_value=0
cm=S.new('ShaderNodeMix'); cm.data_type='RGBA'; SL.new(sn.outputs['Fac'],cm.inputs[0]); cm.inputs[6].default_value=(0.12,0.09,0.06,1); cm.inputs[7].default_value=(0.24,0.19,0.13,1); SL.new(cm.outputs[2],sp.inputs['Base Color'])
SL.new(smr.outputs[0],sp.inputs['Alpha'])
try: sm.blend_method='HASHED'
except Exception: pass
# ---- UVs + soil strips
col=bpy.data.collections.new(COL); sc.collection.children.link(col)
nst=0; nuv=0
for o in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SB_') and o.name.endswith('_UNVERIFIED') and ('_footway_' in o.name or '_pedestrian_' in o.name)]:
    fid=o.name.split('_')[2]; pts=[tuple(p) for p in F[fid]['pts']]; ped='_pedestrian_' in o.name; HW=2.5 if ped else 1.0
    me=o.data; uvl=me.uv_layers.new(name='sc_sl'); mw=o.matrix_world
    for f in me.polygons:
        for li in f.loop_indices:
            co=mw@me.vertices[me.loops[li].vertex_index].co; s,a=proj(pts,co.x,co.y); uvl.data[li].uv=(s/HW,a); nuv+=1
    o.material_slots[0].material=(mp if ped else m)
    # soil strips from top boundary edges
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(mw); bm.normal_update()
    out=bmesh.new(); suvl=out.loops.layers.uv.new('sc_soil'); ouv=out.loops.layers.uv.new('ortho')
    for e in bm.edges:
        tops=[f for f in e.link_faces if f.normal.z>0.7]
        if len(tops)!=1 or len(e.link_faces)<2: continue
        f=tops[0]; a,b=e.verts[0].co,e.verts[1].co; d=Vector((b.x-a.x,b.y-a.y,0))
        if d.length<0.05: continue
        d.normalize(); n=Vector((-d.y,d.x,0)); c=f.calc_center_median()
        mid=(a+b)/2
        if n.dot(Vector((mid.x-c.x,mid.y-c.y,0)))<0: n=-n
        W=0.22; vs=[]
        for p,q in ((a,0),(b,0),(b,1),(a,1)):
            x,y=p.x+n.x*W*q,p.y+n.y*W*q; z=gz(x,y)
            if z is None: z=p.z-0.06
            vs.append(out.verts.new((x,y,z+0.012)))
        ff=out.faces.new(vs)
        for lp,(qa,qb) in zip(ff.loops,((0,0),(0,0),(1,0),(1,0))): lp[suvl].uv=(qa,qb)
        nst+=1
    bm.free()
    if nst==0: out.free(); continue
    bmesh.ops.recalc_face_normals(out,faces=out.faces)
    for ff in out.faces:
        if ff.normal.z<0: ff.normal_flip()
    sme=bpy.data.meshes.new('SC_soil_'+fid); out.to_mesh(sme); out.free(); sme.materials.append(sm)
    so=bpy.data.objects.new('SC_soil_edge_%s_UNVERIFIED'%fid,sme); col.objects.link(so); so['UNVERIFIED_sc']='worn soil strip, visual approximation'
print('SC uv loops',nuv,'soil quads',nst)
# ---- camera: low close-up on the promenade looking along it toward the Annex
pp=[tuple(p) for p in F['313023297']['pts']]
ax,ay=pp[len(pp)//2]; bx,by=pp[len(pp)//2+1]; L=math.hypot(bx-ax,by-ay) or 1; dx,dy=(bx-ax)/L,(by-ay)/L
cx,cy=ax-dx*6+dy*1.2,ay-dy*6-dx*1.2; z0=gz(cx,cy) or 140
cd=bpy.data.cameras.new('SC_CAM_closeup_promenade_joints'); cd.lens=30; cam=bpy.data.objects.new('SC_CAM_closeup_promenade_joints',cd); col.objects.link(cam)
cam.location=(cx,cy,z0+1.3); tx,ty=ax+dx*4,ay+dy*4; tz=(gz(tx,ty) or z0)
cam.rotation_euler=(Vector((tx,ty,tz))-cam.location).to_track_quat('-Z','Y').to_euler()
print('SC cam',tuple(round(c,2) for c in cam.location),'->',(round(tx,2),round(ty,2)))
if os.environ.get('SCSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
