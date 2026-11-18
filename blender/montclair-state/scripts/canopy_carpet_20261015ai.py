"""2026-10-15 ~4:40 AM ET, tag 20261015ai. RERUNNABLE (removes its own collection first). --save to write.
Canopy carpet across the CCOM lab view wedge (bearing -72..+2 deg from the lab skyline cam, 450 m-6.5 km),
driven by NLCD 2021 Tree Canopy Cover (30 m, USFS/MRLC, public domain): crowns per 30 m cell = canopy fraction x cell / crown area.
Cell canopy fraction MEASURED; crown xy within cell, size, height UNVERIFIED. OSM houses + street corridors excluded.
Geometry-nodes instancing of the shared ag/ah crown + trunk meshes (memory-light). No lamps / street furniture."""
import bpy, json, math, os, sys, random, bmesh
from mathutils import Vector
SAVE="--save" in sys.argv; TAG="20261015ai"; ROOT=bpy.path.abspath("//")
J=os.path.join(ROOT,"data","ccom_mid_distance","ai","canopy_carpet_points_20261015ai.json")
COL=f"MID_canopy_carpet_{TAG}"; PCOL=f"MID_canopy_carpet_protos_{TAG}"
rng=random.Random(2026101544)
for ng in [g for g in bpy.data.node_groups if g.name.startswith("MID_canopy_carpet_") and "_ai_GN" in g.name]: bpy.data.node_groups.remove(ng)
for cn in (COL,PCOL):
    c=bpy.data.collections.get(cn)
    if c:
        for o in list(c.all_objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
st=bpy.data.collections["MID_street_trees_20261015ag"]
crown=next(o for o in st.objects if o.type=='MESH')
tr=bpy.data.collections["MID_street_trunks_20261015ah"]; trunk=next(o for o in tr.objects if o.type=='MESH')
print("protos", crown.name, crown.data.name, trunk.name, trunk.data.name)
col=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(col)
pcol=bpy.data.collections.new(PCOL); col.children.link(pcol)
def proto(name,mesh):
    o=bpy.data.objects.new(name,mesh); pcol.objects.link(o); return o
cm=crown.data.copy(); cm.name="MID_canopy_carpet_crown_mesh_ai"
src_mat=crown.data.materials[0] if crown.data.materials else None
if src_mat:
    old=bpy.data.materials.get("MID_canopy_carpet_leaf_ai")
    if old: bpy.data.materials.remove(old)
    nm=src_mat.copy(); nm.name="MID_canopy_carpet_leaf_ai"
    import colorsys
    for n in nm.node_tree.nodes:
        if n.type=='VALTORGB':
            for i,e in enumerate(n.color_ramp.elements):
                h,sat,v=colorsys.rgb_to_hsv(*e.color[:3]); h=min(max(h+(-0.012,0.0,0.02,0.035)[i%4],0.18),0.33)
                r,g,b=colorsys.hsv_to_rgb(h,min(1.0,sat*1.25),v*0.72); e.color=(r,g,b,1.0)
            print("ramp", [tuple(round(c,3) for c in e.color[:3]) for e in n.color_ramp.elements])
    cm.materials.clear(); cm.materials.append(nm)
pc=proto("MID_canopy_carpet_proto_crown_ai",cm); pt=proto("MID_canopy_carpet_proto_trunk_ai",trunk.data)
def bbox(m):
    xs=[v.co for v in m.vertices]; return Vector((min(v.x for v in xs),min(v.y for v in xs),min(v.z for v in xs))),Vector((max(v.x for v in xs),max(v.y for v in xs),max(v.z for v in xs)))
cmin,cmax=bbox(crown.data); tmin,tmax=bbox(trunk.data)
c_hr=max(cmax.x-cmin.x,cmax.y-cmin.y)/2; c_vr=(cmax.z-cmin.z)/2; c_cz=(cmax.z+cmin.z)/2
t_r=max(tmax.x-tmin.x,tmax.y-tmin.y)/2; t_h=tmax.z-tmin.z
print("crown hr vr cz",c_hr,c_vr,c_cz,"trunk r h zmin",t_r,t_h,tmin.z)
# exclude proto layer collection from view layer (objects still usable by Object Info)
def find_lc(lc,n):
    if lc.collection.name==n: return lc
    for ch in lc.children:
        r=find_lc(ch,n)
        if r: return r
find_lc(bpy.context.view_layer.layer_collection,PCOL).exclude=True
G=[bpy.data.objects[n] for n in ("Context_skirt_3DEP_ortho_4km","BD_farfield_3DEP_ortho","Context_ground_beyond_data") if n in bpy.data.objects]
inv=[(o,o.matrix_world.inverted()) for o in G]
def gz(x,y):
    best=None
    for o,mi in inv:
        ok,loc,nor,idx=o.ray_cast(mi@Vector((x,y,3000.0)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            z=(o.matrix_world@loc).z; best=z if best is None else max(best,z)
    return best
P=json.load(open(J))["points"]
J2=J.replace("canopy_carpet_points_","canopy_carpet_points_far2_")
if os.path.exists(J2):
    for q in json.load(open(J2))["points"]: q["far2"]=True; P.append(q)
near_c=[];near_t=[];far_c=[];far2_c=[]; miss=0
for p in P:
    z=gz(p["x"],p["y"])
    if z is None: miss+=1; continue
    hr=p["rad"]*(1.30 if p["near"] else 1.25)*rng.choice((0.8,0.9,1.0,1.0,1.1,1.25,1.45)); rz=rng.uniform(0,6.283)
    ax,ay=rng.uniform(0.85,1.15),rng.uniform(0.85,1.15)
    if p["near"]:
        vr=hr*rng.uniform(0.62,0.9); base=rng.uniform(2.4,4.4); cz=z+base+vr
        near_c.append(((p["x"],p["y"],cz),(ax*hr/c_hr,ay*hr/c_hr,vr/c_vr),rz))
        th=base+vr*0.6; trr=min(0.38,0.12+hr*0.035)
        near_t.append(((p["x"],p["y"],z-0.3),(trr/t_r,trr/t_r,(th+0.3)/t_h),rz))
    else:
        vr=hr*rng.uniform(0.45,0.62); cz=z+rng.uniform(3.5,5.5)+vr
        (far2_c if p.get("far2") else far_c).append(((p["x"],p["y"],cz),(ax*hr/c_hr,ay*hr/c_hr,vr/c_vr),rz))
print("near",len(near_c),"far",len(far_c),"far2",len(far2_c),"miss",miss)
def ptobj(name,data,src,zoff):
    me=bpy.data.meshes.new(name+"_pts"); me.from_pydata([(a[0][0],a[0][1],a[0][2]-zoff) for a in data],[],[])
    a_s=me.attributes.new("sc",'FLOAT_VECTOR','POINT'); a_r=me.attributes.new("rot",'FLOAT_VECTOR','POINT')
    a_s.data.foreach_set("vector",[v for a in data for v in a[1]]); a_r.data.foreach_set("vector",[v for a in data for v in (rng.uniform(-0.07,0.07),rng.uniform(-0.07,0.07),a[2])])
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    ng=bpy.data.node_groups.new(name+"_GN",'GeometryNodeTree')
    ng.interface.new_socket("Geometry",in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket("Geometry",in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput'); iop=N.new('GeometryNodeInstanceOnPoints')
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=src; oi.transform_space='ORIGINAL'
    s=N.new('GeometryNodeInputNamedAttribute'); s.data_type='FLOAT_VECTOR'; s.inputs['Name'].default_value="sc"
    r=N.new('GeometryNodeInputNamedAttribute'); r.data_type='FLOAT_VECTOR'; r.inputs['Name'].default_value="rot"
    L.new(gi.outputs[0],iop.inputs['Points']); L.new(oi.outputs['Geometry'],iop.inputs['Instance'])
    L.new(s.outputs['Attribute'],iop.inputs['Scale']); L.new(r.outputs['Attribute'],iop.inputs['Rotation'])
    L.new(iop.outputs['Instances'],go.inputs[0])
    md=o.modifiers.new("GN",'NODES'); md.node_group=ng
    o.cycles.use_camera_cull=True; o.cycles.use_distance_cull=True
    o["ai_status"]="NLCD 2021 TCC cell fraction MEASURED; crown xy-in-cell/size/height UNVERIFIED"
    return o
# instance origin: crown mesh centred at c_cz -> shift points so crown centre lands at cz (scale applies around proto origin)
def shifted(data,cz0,sz_idx):
    return [((a[0][0],a[0][1],a[0][2]-cz0*a[1][2]),a[1],a[2]) for a in data]
ptobj("MID_canopy_carpet_near_crowns_ai",shifted(near_c,c_cz,2),pc,0.0)
ptobj("MID_canopy_carpet_far_crowns_ai",shifted(far_c,c_cz,2),pc,0.0)
if far2_c: ptobj("MID_canopy_carpet_far2_crowns_ai",shifted(far2_c,c_cz,2),pc,0.0)
ptobj("MID_canopy_carpet_near_trunks_ai",shifted(near_t,tmin.z,2),pt,0.0)
col["ai_note"]="Canopy carpet 20261015ai; source NLCD 2021 TCC (USFS/MRLC public domain)"
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")
