# om (Oct 31 2026): Schmitt follow-ups from ol's Next list, all UNVERIFIED (no photo of these details):
# (1) lift T_RedMaple_L1_0511 (+0.15 m) and Lamp_acorn_049 (+0.03 m) so their bases no longer start under the ol island lawn cap;
# (2) the small walk-island cap (21.6,136.5) gets its own lawn-tone copy of Ground_ortho_grass (pale, sand-like ortho tone -> lawn);
# (3) curb control joints (dark 1 cm grooves at segment joints + every ~1.5 m) on the ol curb;
# (4) soft drip/grime shadow decals under the 133 ok cast-stone sills (3 mm off the wall, shadows off);
# (5) per-window blind drop variation on Schmitt: the shared blind material gets a location-hashed random inside the Schmitt bbox
#     (Object Info Random gave one value for every instance); outside the bbox the original Random path is kept (CCOM unchanged).
# OSM/LiDAR not edited. REVERT=1 restores everything (positions, material slots, blind material).
import bpy, bmesh, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OM_Schmitt_curb_joints_sill_drips_20261031om'
MOVES={'T_RedMaple_L1_0511':0.15,'Lamp_acorn_049':0.03}
ORIGZ={'T_RedMaple_L1_0511':137.742,'Lamp_acorn_049':None}
MI='OM_Schmitt_small_island_lawn_tone_UNVERIFIED'; MJ='OM_Schmitt_curb_joint_dark_UNVERIFIED'; MD='OM_Schmitt_sill_drip_grime_UNVERIFIED'
MB='OM_Schmitt_win_blind_var_UNVERIFIED'
sc=bpy.context.scene
# --- clean
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
cap=bpy.data.objects['OL_Schmitt_walk_island_lawn_caps']
if MI in [m.name for m in cap.data.materials if m]:
    for p in cap.data.polygons: p.material_index=0
    cap.data.materials.pop(index=1)
bl=bpy.data.objects['CCOM_Win_Wing_A_blind'].data
if bl.materials[0] and bl.materials[0].name==MB: bl.materials[0]=bpy.data.materials['CCOM_win_blind']
for n in (MI,MJ,MD,MB):
    m=bpy.data.materials.get(n)
    if m: bpy.data.materials.remove(m)
for n,dz in MOVES.items():
    o=bpy.data.objects[n]
    if 'om_orig_z' in o: o.location.z=o['om_orig_z']; del o['om_orig_z']
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
# (1)
for n,dz in MOVES.items():
    o=bpy.data.objects[n]; o['om_orig_z']=o.location.z; o.location.z+=dz
# (2)
g=bpy.data.materials['Ground_ortho_grass']; mi=g.copy(); mi.name=MI
nt=mi.node_tree; out=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'][0]
# find the base colour feeding the principled BSDF and tint it toward lawn
pb=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED']
if pb:
    p=pb[0]; s=p.inputs['Base Color']
    if s.is_linked:
        src=s.links[0].from_socket
        hsv=nt.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Hue'].default_value=0.5; hsv.inputs['Saturation'].default_value=0.7; hsv.inputs['Value'].default_value=0.8
        mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MIX'; mx.inputs['Factor'].default_value=0.55
        mx.inputs[7].default_value=(0.12,0.17,0.07,1)
        nt.links.new(src,hsv.inputs['Color']); nt.links.new(hsv.outputs[0],mx.inputs[6]); nt.links.new(mx.outputs[2],s)
print('island mat principled',len(pb))
cap.data.materials.append(mi); ns=0
for p in cap.data.polygons:
    cc=p.center
    if (Vector((cc.x,cc.y))-Vector((21.6,136.5))).length<9: p.material_index=1; ns+=1
print('small island faces',ns)
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
# (3) curb joints
cu=bpy.data.objects['OL_Schmitt_entrance_walk_edge_curb'].data
mj=bpy.data.materials.new(MJ); mj.use_nodes=True; pj=mj.node_tree.nodes['Principled BSDF']; pj.inputs['Base Color'].default_value=(0.13,0.13,0.12,1); pj.inputs['Roughness'].default_value=0.95
bm=bmesh.new(); nj=0
for k in range(len(cu.vertices)//8):
    v=[cu.vertices[8*k+j].co.copy() for j in range(8)]
    # order: a_in_top0,a_in_bot1,a_out_top2,a_out_bot3,b_in_top4,b_in_bot5,b_out_top6,b_out_bot7
    a_in,a_out,b_in,b_out=v[0],v[2],v[4],v[6]
    L=(b_in-a_in).length; t=(b_in-a_in).normalized(); m=max(1,round(L/1.5))
    for i in range(m):
        f=(0.03+i*(L-0.06)/m)/L if i==0 else i/m
        pin=a_in.lerp(b_in,f); pout=a_out.lerp(b_out,f); nrm=(pout-pin); nrm.z=0; nrm.normalize()
        w=t*0.008; up=Vector((0,0,0.002))
        q=[pin-w+up,pin+w+up,pout+nrm*0.003-w+up,pout+nrm*0.003+w+up]
        q2=[pout+nrm*0.003-w,pout+nrm*0.003+w]
        vs=[bm.verts.new(x) for x in q]; vb=[bm.verts.new(x+Vector((0,0,-0.16))) for x in q2]
        bm.faces.new([vs[0],vs[1],vs[3],vs[2]]); bm.faces.new([vs[2],vs[3],vb[1],vb[0]]); nj+=1
mej=bpy.data.meshes.new('OM_Schmitt_curb_control_joints'); bm.to_mesh(mej); mej.materials.append(mj)
oj=bpy.data.objects.new('OM_Schmitt_curb_control_joints',mej); col.objects.link(oj); oj.visible_shadow=False; oj['UNVERIFIED']='om: curb joints spacing guessed'
print('joints',nj)
# (4) sill drips
s=bpy.data.objects['OK_Schmitt_punched_window_cast_stone_sills'].data
dg=bpy.context.evaluated_depsgraph_get()
md=bpy.data.materials.new(MD); md.use_nodes=True; nt=md.node_tree; p=nt.nodes['Principled BSDF']
p.inputs['Base Color'].default_value=(0.07,0.065,0.055,1); p.inputs['Roughness'].default_value=0.95
tc=nt.nodes.new('ShaderNodeTexCoord'); sx=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['UV'],sx.inputs[0])
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=4; nz.inputs['Detail'].default_value=2
mpv=nt.nodes.new('ShaderNodeMapping'); mpv.inputs['Scale'].default_value=(6,1,1); nt.links.new(tc.outputs['UV'],mpv.inputs[0]); nt.links.new(mpv.outputs[0],nz.inputs['Vector'])
pw=nt.nodes.new('ShaderNodeMath'); pw.operation='POWER'; pw.inputs[1].default_value=0.9; nt.links.new(sx.outputs['Y'],pw.inputs[0])
m1=nt.nodes.new('ShaderNodeMath'); m1.operation='MULTIPLY'; nt.links.new(pw.outputs[0],m1.inputs[0]); nt.links.new(nz.outputs['Fac'],m1.inputs[1])
m2=nt.nodes.new('ShaderNodeMath'); m2.operation='MULTIPLY'; m2.inputs[1].default_value=1.2; m2.use_clamp=True; nt.links.new(m1.outputs[0],m2.inputs[0])
# side fade (x near 0/1)
sx2=nt.nodes.new('ShaderNodeMath'); sx2.operation='PINGPONG'; sx2.inputs[1].default_value=0.5; nt.links.new(sx.outputs['X'],sx2.inputs[0])
sf=nt.nodes.new('ShaderNodeMapRange'); sf.inputs[1].default_value=0.0; sf.inputs[2].default_value=0.12; nt.links.new(sx2.outputs[0],sf.inputs[0])
m3=nt.nodes.new('ShaderNodeMath'); m3.operation='MULTIPLY'; nt.links.new(m2.outputs[0],m3.inputs[0]); nt.links.new(sf.outputs[0],m3.inputs[1])
nt.links.new(m3.outputs[0],p.inputs['Alpha'])
bm=bmesh.new(); uvs=[]; nd=0; nskip=0
for k in range(len(s.vertices)//8):
    v=[s.vertices[8*k+j].co.copy() for j in range(8)]
    a,b,c2=v[0],v[1],v[2]
    along=b-a; dep=c2-b; zb=a.z
    if along.length<dep.length: along,dep=dep,along
    cen=sum(v,Vector())/8; dn=dep.normalized(); dn.z=0; dn.normalize()
    # inward = direction whose ray hits a wall within 0.5 m of the sill centre at 3 cm below the sill
    o0=Vector((cen.x,cen.y,zb-0.05)); free=[]
    for sgn in (1,-1):
        d=dn*sgn; hit,loc,nrm,idx,hob,mm=sc.ray_cast(dg,o0,d,distance=2.0)
        free.append(((loc-o0).length if hit else 2.0,d))
    free.sort(key=lambda x:-x[0]); out_d=free[0][1]
    if free[0][0]<0.8: nskip+=1; continue
    st=o0+out_d*0.8; hit,loc,nrm,idx,hob,mm=sc.ray_cast(dg,st,-out_d,distance=1.2)
    if not hit: nskip+=1; continue
    wall_off=(loc-o0).dot(out_d)+0.003; d=out_d
    ac=along.normalized(); half=along.length*0.47
    base=Vector((cen.x,cen.y,zb))+d*wall_off
    H=0.22+0.12*((k*37)%11)/10
    pts=[base-ac*half, base+ac*half, base+ac*half*0.9-Vector((0,0,H)), base-ac*half*0.9-Vector((0,0,H))]
    vs=[bm.verts.new(x) for x in pts]; f=bm.faces.new(vs); uvs.append(((0,1),(1,1),(1,0),(0,0))); nd+=1
me=bpy.data.meshes.new('OM_Schmitt_sill_drip_grime'); bm.to_mesh(me)
ul=me.uv_layers.new(name='UVMap')
for pi,poly in enumerate(me.polygons):
    for j,li in enumerate(poly.loop_indices): ul.data[li].uv=uvs[pi][j]
me.materials.append(md)
od=bpy.data.objects.new('OM_Schmitt_sill_drip_grime',me); col.objects.link(od); od.visible_shadow=False; od['UNVERIFIED']='om: sill drip grime typical, no photo'
print('drips',nd,'skipped',nskip)
# (5) blind variation
mb=bpy.data.materials['CCOM_win_blind'].copy(); mb.name=MB; nt=mb.node_tree
mr=nt.nodes['Map Range']; oi=nt.nodes['Object Info']
wn=nt.nodes.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions='3D'
sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(oi.outputs['Location'],sep.inputs[0]); nt.links.new(oi.outputs['Location'],wn.inputs['Vector'])
def rng(sock,lo,hi):
    a=nt.nodes.new('ShaderNodeMath'); a.operation='GREATER_THAN'; a.inputs[1].default_value=lo; nt.links.new(sock,a.inputs[0])
    b=nt.nodes.new('ShaderNodeMath'); b.operation='LESS_THAN'; b.inputs[1].default_value=hi; nt.links.new(sock,b.inputs[0])
    m=nt.nodes.new('ShaderNodeMath'); m.operation='MULTIPLY'; nt.links.new(a.outputs[0],m.inputs[0]); nt.links.new(b.outputs[0],m.inputs[1]); return m.outputs[0]
gx=rng(sep.outputs['X'],-30,25); gy=rng(sep.outputs['Y'],108,194)
gm=nt.nodes.new('ShaderNodeMath'); gm.operation='MULTIPLY'; nt.links.new(gx,gm.inputs[0]); nt.links.new(gy,gm.inputs[1])
mxr=nt.nodes.new('ShaderNodeMix'); mxr.data_type='FLOAT'
nt.links.new(gm.outputs[0],mxr.inputs['Factor']); nt.links.new(oi.outputs['Random'],mxr.inputs[2]); nt.links.new(wn.outputs['Value'],mxr.inputs[3])
nt.links.new(mxr.outputs[0],mr.inputs['Value'])
bl.materials[0]=mb
print('blind var on, mesh users',bl.users)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
