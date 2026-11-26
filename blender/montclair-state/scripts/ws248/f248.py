# ws248 (W62f): east-stand back walk follow-up, CHAIN pass on main (merge208).
# 1) 1:2 gravel fill wedge under the back of the stand from h248.json (walk W edge stood up to 1.25 m over the ground under the stand).
# 2) walk joints: UV 'WS248_along' (u = across m, v = along-path m) + material copy of Paving_concrete with 1.524 m (5 ft)
#    transverse saw-cut lines from that UV (Paving_concrete's own world 1.5 m grid is switched off: Math.024 x 0).
# 3) the walk's edge skirts get Greenhouse_BaseWall_Concrete (same as the WS243 stand edge walls) instead of the top
#    paving image projected onto vertical faces.
import bpy, json, numpy as np
TAG='F248'; WN='WS247_E_stand_back_walk_ortho2020_UNVERIFIED_level'; NM='WS248_E_stand_back_gravel_fill_1in2_UNVERIFIED'
wk=bpy.data.objects[WN]; me=wk.data
if NM not in bpy.data.objects:
    J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws248/h248.json'))
    m2=bpy.data.meshes.new(NM); m2.from_pydata(J['V'],[],[tuple(f) for f in J['F']]); m2.validate(); m2.update()
    for p in m2.polygons: p.use_smooth=False
    gm=bpy.data.materials.get('fr_under_gravel') or bpy.data.materials['MN_underdeck_gravel_dark_UNVERIFIED']; m2.materials.append(gm)
    o=bpy.data.objects.new(NM,m2)
    for c in wk.users_collection: c.objects.link(o)
    uv=m2.uv_layers.new(name='UVMap')
    for p in m2.polygons:
        for li in p.loop_indices:
            v=m2.vertices[m2.loops[li].vertex_index].co; uv.data[li].uv=(v.x/2.0,v.y/2.0)
    print(TAG,'wedge',NM,len(m2.vertices),len(m2.polygons),gm.name,flush=True)
# UV along
V=np.array([v.co[:] for v in me.vertices]); R=V.reshape(-1,6,3); C=(R[:,1,:2]+R[:,2,:2])/2
s=np.concatenate(([0],np.cumsum(np.linalg.norm(np.diff(C,axis=0),axis=1))))
ua={}
for i,r in enumerate(R):
    e0=r[0,:2]
    for k in range(6):
        p=r[k,:2] if k<4 else (r[0,:2] if k==4 else r[3,:2])
        ua[i*6+k]=(float(np.linalg.norm(p-e0)),float(s[i]+0.40))   # +0.40: first joint 1.12 m in from the S end
L=me.uv_layers.get('WS248_along') or me.uv_layers.new(name='WS248_along')
for p in me.polygons:
    for li in p.loop_indices: L.data[li].uv=ua[me.loops[li].vertex_index]
# material
base=bpy.data.materials['Paving_concrete']; JN='WS248_Paving_concrete_walk_joints_1p524m_UV'
jm=bpy.data.materials.get(JN)
if jm is None:
    jm=base.copy(); jm.name=JN; nt=jm.node_tree; N=nt.nodes; Lk=nt.links
    bs=N['Principled Behind'] if 'Principled Behind' in N else N['Principled BSDF']
    src=bs.inputs['Base Color'].links[0].from_socket; nsrc=bs.inputs['Normal'].links[0].from_socket if bs.inputs['Normal'].links else None
    uvn=N.new('ShaderNodeUVMap'); uvn.uv_map='WS248_along'
    sp=N.new('ShaderNodeSeparateXYZ'); Lk.new(uvn.outputs['UV'],sp.inputs[0])
    def M(op,a,b=None):
        n=N.new('ShaderNodeMath'); n.operation=op
        (Lk.new(a,n.inputs[0]) if not isinstance(a,(int,float)) else n.inputs[0].__setattr__('default_value',a))
        if b is not None: (Lk.new(b,n.inputs[1]) if not isinstance(b,(int,float)) else n.inputs[1].__setattr__('default_value',b))
        return n.outputs[0]
    f=M('FRACT',M('DIVIDE',sp.outputs['Y'],1.524))
    d=M('MULTIPLY',M('MINIMUM',f,M('SUBTRACT',1.0,f)),1.524)            # metres to the nearest joint
    mask=M('LESS_THAN',d,0.007)                                          # ~14 mm saw cut
    # tooled edge band 4 cm in from each long edge (common on poured walks; reads as the slab edge)
    u=sp.outputs['X']; edge=M('MAXIMUM',M('LESS_THAN',M('ABSOLUTE',M('SUBTRACT',u,0.06)),0.006),M('LESS_THAN',M('ABSOLUTE',M('SUBTRACT',u,2.74)),0.006))
    mk=M('MAXIMUM',mask,edge)
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'
    Lk.new(M('MULTIPLY',mk,0.75),mx.inputs['Factor']); Lk.new(src,mx.inputs[6]); mx.inputs[7].default_value=(0.42,0.40,0.37,1)
    Lk.new(mx.outputs[2],bs.inputs['Base Color'])
    bp=N.new('ShaderNodeBump'); bp.invert=True; bp.inputs['Strength'].default_value=0.35; bp.inputs['Distance'].default_value=0.004
    Lk.new(mk,bp.inputs['Height'])
    if nsrc: Lk.new(nsrc,bp.inputs['Normal'])
    Lk.new(bp.outputs['Normal'],bs.inputs['Normal'])
    print(TAG,'material',JN,'from',src.node.name,'normal from',nsrc.node.name if nsrc else None,flush=True)
wm=bpy.data.materials['Greenhouse_BaseWall_Concrete']
me.materials.clear(); me.materials.append(jm); me.materials.append(wm)
ns=0
for i,p in enumerate(me.polygons):
    k=i%5; p.material_index=1 if k>=3 else 0; ns+=(k>=3)
print(TAG,'walk mats',[m.name for m in me.materials],'skirt faces',ns,'of',len(me.polygons),'along len',round(float(s[-1]),1),flush=True)
nz=sum(1 for i,p in enumerate(me.polygons) if i%5>=3 and abs(p.normal.z)<0.6); nt_=sum(1 for i,p in enumerate(me.polygons) if i%5<3 and p.normal.z>0.9)
print(TAG,'check skirt faces near-vertical',nz,'top faces up',nt_,flush=True)
