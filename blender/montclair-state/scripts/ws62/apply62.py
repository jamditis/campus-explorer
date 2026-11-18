# ws62: break up the woods canopy carpet silhouette. (1) the 3 picked crown protos become multi-lobe clustered crowns
# (5-6 jittered lobes, ~70 verts, same bbox) with a per-vertex 'shade' attribute (darker undersides/crevices);
# (2) GN: per-instance size + height variation, ~12% gaps in far/far2 carpets; (3) material: shade darkening,
# leaf-clump value noise, stronger bump. Idempotent (tagged by mesh names WS62_*). SAVE=1 to save.
import bpy, bmesh, random, math, os
from mathutils import Vector
done=bpy.data.meshes.get('WS62_crown_lumpy') is not None
def build(name, seed, zmin, zmax, nlobes):
    rnd=random.Random(seed); bm=bmesh.new(); centers=[]
    lobes=[(Vector((0,0,0.12)),0.62)]
    for k in range(nlobes-1):
        a=2*math.pi*k/(nlobes-1)+rnd.uniform(-0.4,0.4); d=rnd.uniform(0.38,0.58)
        lobes.append((Vector((d*math.cos(a),d*math.sin(a),rnd.uniform(-0.18,0.32))),rnd.uniform(0.36,0.52)))
    for c,r in lobes:
        g=bmesh.ops.create_icosphere(bm,subdivisions=1,radius=r)
        for v in g['verts']:
            v.co=v.co*(1+rnd.uniform(-0.12,0.12))+c
        centers.append((c,r))
    vs=list(bm.verts)
    mn=Vector([min(v.co[i] for v in vs) for i in range(3)]); mx=Vector([max(v.co[i] for v in vs) for i in range(3)])
    lo=Vector((-1,-1,zmin)); hi=Vector((1,1,zmax))
    for v in vs:
        for i in range(3): v.co[i]=lo[i]+(v.co[i]-mn[i])/(mx[i]-mn[i])*(hi[i]-lo[i])
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=False
    at=me.attributes.new('shade','FLOAT','POINT')
    for i,v in enumerate(me.vertices):
        h=(v.co.z-zmin)/(zmax-zmin); rad=math.hypot(v.co.x,v.co.y)
        s=0.75*(1-h)**1.6 + (0.25 if (rad<0.55 and h<0.75) else 0) + rnd.uniform(0,0.12)
        at.data[i].value=min(1.0,s)
    return me
if not done:
    spec={'MID_canopy_carpet_proto_crown_lumpy_bl':('WS62_crown_lumpy',621,-0.55,0.96,6),
          'MID_canopy_carpet_proto_crown_broad_bl':('WS62_crown_broad',622,-0.51,0.63,6),
          'MID_canopy_carpet_proto_crown_ico_ref_bl':('WS62_crown_tall',623,-0.55,1.05,5)}
    for on,(mn,sd,z0,z1,nl) in spec.items():
        ob=bpy.data.objects[on]; me=build(mn,sd,z0,z1,nl); me.materials.append(bpy.data.materials['MID_canopy_carpet_leaf_ai']); ob.data=me
    # GN
    def rv(nt,name,dtype,mn,mx,seed,loc):
        n=nt.nodes.new('FunctionNodeRandomValue'); n.name=name; n.data_type=dtype; n.location=loc
        ins={s.identifier:s for s in n.inputs}
        if dtype=='FLOAT': ins['Min_001'].default_value=mn; ins['Max_001'].default_value=mx
        if dtype=='BOOLEAN': ins['Probability'].default_value=mn
        ins['Seed'].default_value=seed; return n
    def outv(n):
        return {s.identifier:s for s in n.outputs}
    for gname,(smin,smax,zmn,zmx,keep) in {'MID_canopy_carpet_far_crowns_ai_GN':(0.72,1.32,0.78,1.38,0.88),
                                        'MID_canopy_carpet_far2_crowns_ai_GN':(0.72,1.32,0.78,1.38,0.88),
                                        'MID_canopy_carpet_near_crowns_ai_GN':(0.85,1.18,0.88,1.22,None)}.items():
        nt=bpy.data.node_groups[gname]; eq=nt.nodes['EQ_scale_Instance on Points']; outn=nt.nodes['Group Output']
        r1=rv(nt,'WS62_rs','FLOAT',smin,smax,6201,(eq.location.x,eq.location.y-250))
        r2=rv(nt,'WS62_rz','FLOAT',zmn,zmx,6202,(eq.location.x,eq.location.y-420))
        mz=nt.nodes.new('ShaderNodeMath'); mz.operation='MULTIPLY'; mz.name='WS62_mz'
        cx=nt.nodes.new('ShaderNodeCombineXYZ'); cx.name='WS62_cx'
        nt.links.new(outv(r1)['Value_001'],mz.inputs[0]); nt.links.new(outv(r2)['Value_001'],mz.inputs[1])
        nt.links.new(outv(r1)['Value_001'],cx.inputs[0]); nt.links.new(outv(r1)['Value_001'],cx.inputs[1]); nt.links.new(mz.outputs[0],cx.inputs[2])
        sc=nt.nodes.new('GeometryNodeScaleInstances'); sc.name='WS62_scale'; sc.location=(eq.location.x+200,eq.location.y)
        sc.inputs['Local Space'].default_value=True
        nt.links.new(eq.outputs[0],sc.inputs['Instances']); nt.links.new(cx.outputs[0],sc.inputs['Scale'])
        nt.links.new(sc.outputs[0],outn.inputs[0])
        if keep:
            rb=rv(nt,'WS62_keep','BOOLEAN',keep,0,6203,(eq.location.x-400,eq.location.y-250))
            nt.links.new(outv(rb)['Value_003'],nt.nodes['Instance on Points'].inputs['Selection'])
    # material
    nt=bpy.data.materials['MID_canopy_carpet_leaf_ai'].node_tree; N=nt.nodes; L=nt.links
    at=N.new('ShaderNodeAttribute'); at.name='WS62_shade_attr'; at.attribute_type='GEOMETRY'; at.attribute_name='shade'
    m1=N.new('ShaderNodeMapRange'); m1.name='WS62_shade_mr'; m1.inputs['To Min'].default_value=1.0; m1.inputs['To Max'].default_value=0.38
    m2=N.new('ShaderNodeMapRange'); m2.name='WS62_clump_mr'; m2.inputs['From Min'].default_value=0.35; m2.inputs['From Max'].default_value=0.65; m2.inputs['To Min'].default_value=0.68; m2.inputs['To Max'].default_value=1.15
    mu=N.new('ShaderNodeMath'); mu.name='WS62_mul'; mu.operation='MULTIPLY'
    vs=N.new('ShaderNodeVectorMath'); vs.name='WS62_scale'; vs.operation='SCALE'
    L.new(at.outputs['Fac'],m1.inputs['Value']); L.new(N['EO_noise'].outputs['Fac'],m2.inputs['Value'])
    L.new(m1.outputs['Result'],mu.inputs[0]); L.new(m2.outputs['Result'],mu.inputs[1])
    hsv=N['BL_hsv']; hz=N['EO_haze_mix']
    L.new(hsv.outputs['Color'],vs.inputs[0]); L.new(mu.outputs[0],vs.inputs['Scale'])
    L.new(vs.outputs['Vector'],hz.inputs[6])  # A_Color
    N['EO_bump'].inputs['Strength'].default_value=0.85
    print('A62 applied')
else: print('A62 already')
for c in ('CAM_closeup_canopy_carpet_ai',):
    o=bpy.data.objects.get(c); print('CAMLOC',c,tuple(round(x) for x in o.matrix_world.translation) if o else None)
hz=bpy.data.materials['MID_canopy_carpet_leaf_ai'].node_tree.nodes['EO_haze_mix']
print('HZA', [ (i.identifier,i.is_linked,[l.from_node.name for l in i.links]) for i in hz.inputs])
if os.environ.get('SAVE')=='1' and not done:
    bpy.ops.wm.save_mainfile(); print('A62 saved')
