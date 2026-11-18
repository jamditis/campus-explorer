"""tag 20261016bl (RERUNNABLE, --save). Canopy carpet variety (Joe Oct 15: more tree variety in shape/size/colour).
- Adds two extra crown protos (lumpy clumped crown, broad flat-topped crown) next to the ai ico crown and has each
  carpet crown GN pick one of the three at random (instance index from a seeded Random Value).
- Extra per-instance non-uniform scale k (xy 0.85-1.2, z 0.8-1.3) with z-offset so each crown centre stays where ai put it.
- Leaf material: per-instance HSV (hue +/-0.015 inside green, sat 1.05-1.30, value 0.58-0.90 (mean slightly darker: lumpy/broad tops caught more sunlit-top tint)) from white noise of the
  instance location (independent of ah ramp's Object-Info random). Season unchanged (summer vs October still Joe's call).
Positions/heights (NLCD-driven, ai) untouched; trunks untouched. All shape/colour = UNVERIFIED artistic."""
import bpy, bmesh, sys, random, math
from mathutils import Vector, noise
SAVE="--save" in sys.argv
rng=random.Random(20261016)
pc=bpy.data.objects["MID_canopy_carpet_proto_crown_ai"]
pcol=pc.users_collection[0]
zs=[v.co.z for v in pc.data.vertices]; C_CZ=(min(zs)+max(zs))/2
xs=[v.co.x for v in pc.data.vertices]; HR=(max(xs)-min(xs))/2; VR=(max(zs)-min(zs))/2
print("proto c_cz",round(C_CZ,3),"hr",round(HR,3),"vr",round(VR,3))
mat=pc.data.materials[0]
# --- protos collection (idempotent)
PN="MID_canopy_carpet_protos_pick_bl"
old=bpy.data.collections.get(PN)
if old:
    for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(old)
pk=bpy.data.collections.new(PN); pcol.children.link(pk)
def mk(name,fn):
    me=bpy.data.meshes.get(name+"_mesh")
    if me: bpy.data.meshes.remove(me)
    bm=bmesh.new(); bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1.0)
    for v in bm.verts: fn(v)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name+"_mesh"); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=False
    me.materials.append(mat)
    o=bpy.data.objects.new(name,me); pk.objects.link(o); return o
def lumpy(v):
    d=v.co.normalized(); n=noise.noise(d*2.3+Vector((3.1,1.7,0.4)))
    r=1.0+0.22*n+rng.uniform(-0.05,0.05)
    co=d*r; v.co=Vector((co.x*HR,co.y*HR,co.z*VR+C_CZ))
def broad(v):
    d=v.co.normalized(); z=d.z
    if z>0.25: z=0.25+(z-0.25)*0.45      # flattened top (oak/maple-like broad crown)
    r=1.0+0.10*noise.noise(d*3.0)
    v.co=Vector((d.x*HR*1.12*r,d.y*HR*1.12*r,z*VR*0.95*r+C_CZ))
p1=mk("MID_canopy_carpet_proto_crown_lumpy_bl",lumpy)
p2=mk("MID_canopy_carpet_proto_crown_broad_bl",broad)
p0=bpy.data.objects.new("MID_canopy_carpet_proto_crown_ico_ref_bl",pc.data); pk.objects.link(p0)
# --- GN edits
done=0
for on in ("MID_canopy_carpet_near_crowns_ai","MID_canopy_carpet_far_crowns_ai","MID_canopy_carpet_far2_crowns_ai"):
    o=bpy.data.objects.get(on)
    if not o: continue
    ng=o.modifiers[0].node_group; N=ng.nodes; L=ng.links
    for n in [n for n in N if n.name.startswith("BL_")]: N.remove(n)
    iop=next(n for n in N if n.type=='INSTANCE_ON_POINTS')
    gi=next(n for n in N if n.type=='GROUP_INPUT')
    sc=next(n for n in N if n.type=='INPUT_ATTRIBUTE' and n.inputs['Name'].default_value=="sc")
    ci=N.new('GeometryNodeCollectionInfo'); ci.name="BL_ci"; ci.inputs['Collection'].default_value=pk
    ci.inputs['Separate Children'].default_value=True; ci.inputs['Reset Children'].default_value=True; ci.transform_space='ORIGINAL'
    ri=N.new('FunctionNodeRandomValue'); ri.name="BL_ri"; ri.data_type='INT'; ri.inputs['Min'].default_value=0; ri.inputs['Max'].default_value=2; ri.inputs['Seed'].default_value=1016+done
    L.new(ci.outputs['Instances'],iop.inputs['Instance']); iop.inputs['Pick Instance'].default_value=True
    L.new(ri.outputs[2],iop.inputs['Instance Index'])
    rk=N.new('FunctionNodeRandomValue'); rk.name="BL_rk"; rk.data_type='FLOAT_VECTOR'
    rk.inputs[0].default_value=(0.85,0.85,0.80); rk.inputs[1].default_value=(1.20,1.20,1.30); rk.inputs['Seed'].default_value=2016+done
    mul=N.new('ShaderNodeVectorMath'); mul.name="BL_mul"; mul.operation='MULTIPLY'
    L.new(sc.outputs['Attribute'],mul.inputs[0]); L.new(rk.outputs[0],mul.inputs[1]); L.new(mul.outputs[0],iop.inputs['Scale'])
    # z offset so crown centre stays: dz = C_CZ*sc.z*(1-k.z)
    s1=N.new('ShaderNodeSeparateXYZ'); s1.name="BL_s1"; L.new(sc.outputs['Attribute'],s1.inputs[0])
    s2=N.new('ShaderNodeSeparateXYZ'); s2.name="BL_s2"; L.new(rk.outputs[0],s2.inputs[0])
    om=N.new('ShaderNodeMath'); om.name="BL_om"; om.operation='SUBTRACT'; om.inputs[0].default_value=1.0; L.new(s2.outputs['Z'],om.inputs[1])
    m1=N.new('ShaderNodeMath'); m1.name="BL_m1"; m1.operation='MULTIPLY'; L.new(s1.outputs['Z'],m1.inputs[0]); L.new(om.outputs[0],m1.inputs[1])
    m2=N.new('ShaderNodeMath'); m2.name="BL_m2"; m2.operation='MULTIPLY'; m2.inputs[1].default_value=C_CZ; L.new(m1.outputs[0],m2.inputs[0])
    cx=N.new('ShaderNodeCombineXYZ'); cx.name="BL_cx"; L.new(m2.outputs[0],cx.inputs['Z'])
    sp=N.new('GeometryNodeSetPosition'); sp.name="BL_sp"
    lk=[l for l in L if l.to_node==iop and l.to_socket.name=='Points']
    if lk: src=lk[0].from_socket; L.remove(lk[0])
    else: src=gi.outputs[0]   # rerun: BL_sp was removed above
    L.new(src,sp.inputs['Geometry']); L.new(cx.outputs[0],sp.inputs['Offset']); L.new(sp.outputs[0],iop.inputs['Points'])
    o["bl_variety"]="3 protos pick + k scale jitter (UNVERIFIED artistic); xy/height from ai unchanged"
    done+=1
print("GN edited",done)
# --- material per-instance HSV
nt=mat.node_tree; N=nt.nodes; L=nt.links
for n in [n for n in N if n.name.startswith("BL_")]: N.remove(n)
b=next(n for n in N if n.type=='BSDF_PRINCIPLED'); aj=N["AJ_mix"]
oi=N.new('ShaderNodeObjectInfo'); oi.name="BL_oi"
wn=N.new('ShaderNodeTexWhiteNoise'); wn.name="BL_wn"; wn.noise_dimensions='3D'; L.new(oi.outputs['Location'],wn.inputs['Vector'])
sp=N.new('ShaderNodeSeparateColor'); sp.name="BL_sep"; L.new(wn.outputs['Color'],sp.inputs[0])
def mr(name,a,bb,inp):
    m=N.new('ShaderNodeMapRange'); m.name=name; m.inputs['To Min'].default_value=a; m.inputs['To Max'].default_value=bb; L.new(inp,m.inputs['Value']); return m
mh=mr("BL_mh",0.485,0.515,sp.outputs[0]); ms=mr("BL_ms",1.05,1.30,sp.outputs[1]); mv=mr("BL_mv",0.58,0.90,sp.outputs[2])
hsv=N.new('ShaderNodeHueSaturation'); hsv.name="BL_hsv"
L.new(mh.outputs[0],hsv.inputs['Hue']); L.new(ms.outputs[0],hsv.inputs['Saturation']); L.new(mv.outputs[0],hsv.inputs['Value'])
L.new(aj.outputs[2],hsv.inputs['Color']); L.new(hsv.outputs['Color'],b.inputs['Base Color'])
mat["bl_hsv"]="per-instance HSV jitter 20261016bl (UNVERIFIED artistic); season unchanged"
print("MAT ok")
# --- soft light recipe check (read only)
sc_=bpy.context.scene; print("LOOK",sc_.view_settings.look)
for l in bpy.data.lights:
    if l.type=='SUN': print("SUN",l.name,round(math.degrees(l.angle),2),round(l.energy,3))
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")
