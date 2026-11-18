# ou (Oct 31 2026 ~10:35 PM ET): ot 'Next' follow-ups, ALL UNVERIFIED.
# (A) base-course seam: collinear OR base-course boxes overlapped ~8 cm with coplanar faces (faint z-fight seam). Each overlapping collinear
#     pair is trimmed to a butt joint at the overlap midpoint (both ends re-seated on the DTM, -0.22/+0.42), original co kept in attr ou_co0.
# (B) pale context-skirt hillside / straight DTM edge: GN modifier OU_skirt_edge_tone stores 'ou_edge' (1 at the DTM edge -> 0 by 150 m) on the
#     skirt; a copy of the skirt material (OU_Context_skirt_ortho_edge_tone_UNVERIFIED) multiplies the colour toward a darker, greener grass
#     tone there, broken up by noise. Original material kept with a fake user. Skirt mesh unedited.
# (C) cam OU_CAM_closeup_base_course_butt_joint. REVERT=1 undoes everything.
import bpy, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CB='OR_skirt_base_course_20261031or'; SM='Context_skirt_ortho'; NM='OU_Context_skirt_ortho_edge_tone_UNVERIFIED'; GN='OU_skirt_edge_tone'; CC='OU_cams_20261031ou'
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
# ---- undo
c=bpy.data.collections.get(CC)
if c:
    for o in list(c.objects): d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    bpy.data.collections.remove(c)
m=sk.modifiers.get(GN)
if m: sk.modifiers.remove(m)
g=bpy.data.node_groups.get(GN)
if g: bpy.data.node_groups.remove(g)
om=bpy.data.materials[SM]
for i,x in enumerate(sk.data.materials):
    if x and x.name==NM: sk.data.materials[i]=om
x=bpy.data.materials.get(NM)
if x: bpy.data.materials.remove(x)
nr=0
for ob in bpy.data.collections[CB].objects:
    me=ob.data; a=me.attributes.get('ou_co0')
    if a:
        for v,d in zip(me.vertices,a.data): v.co=d.vector
        me.attributes.remove(me.attributes['ou_co0']); me.update(); nr+=1
for k in ('UNVERIFIED_ou',):
    if k in sk: del sk[k]
print('restored',nr)
if REV:
    om.use_fake_user=False; print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
# ---- (A)
dg=bpy.context.evaluated_depsgraph_get(); e=ter.evaluated_get(dg); tm=e.to_mesh(); mw=ter.matrix_world
bt=BVHTree.FromPolygons([mw@v.co for v in tm.vertices],[p.vertices[:] for p in tm.polygons]); e.to_mesh_clear()
def dtm(x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),900); return h[0].z if h[0] else None
joints=[]; npair=0
for ob in bpy.data.collections[CB].objects:
    me=ob.data; W=ob.matrix_world; Wi=W.inverted()
    a=me.attributes.new('ou_co0','FLOAT_VECTOR','POINT')
    for d,v in zip(a.data,me.vertices): d.vector=v.co
    oh=[x.value for x in me.attributes['or_h'].data]
    nb=len(me.vertices)//8; boxes=[]
    for b in range(nb):
        idx=list(range(8*b,8*b+8)); P=[W@me.vertices[i].co for i in idx]
        fp=[me.polygons[f] for f in range(6*b,6*b+6) if abs(me.polygons[f].normal.z)<0.5]
        fn=(W.to_3x3()@max(fp,key=lambda q:q.area).normal); fn.z=0; n=fn.normalized(); u=Vector((n.y,-n.x,0))
        us=[p.dot(u) for p in P]; ns=[p.dot(n) for p in P]
        boxes.append(dict(idx=idx,u=u,n=n,umin=min(us),umax=max(us),nmin=min(ns),nmax=max(ns)))
    for i,A in enumerate(boxes):
        for j,B in enumerate(boxes):
            if j<=i: continue
            if abs(A['u'].dot(B['u']))<0.9995: continue
            s=1 if A['u'].dot(B['u'])>0 else -1
            u=A['u']; n=A['n']
            Bn=[(W@me.vertices[k].co).dot(n) for k in B['idx']]; Bu=[(W@me.vertices[k].co).dot(u) for k in B['idx']]
            if abs(min(Bn)-A['nmin'])>0.01 or abs(max(Bn)-A['nmax'])>0.01: continue
            lo=max(A['umin'],min(Bu)); hi=min(A['umax'],max(Bu))
            if hi<=lo+0.002 or hi-lo>0.6: continue
            mid=(lo+hi)/2; npair+=1
            # which box is on the low side?
            if (A['umin']+A['umax'])<(min(Bu)+max(Bu)): low,high=A['idx'],B['idx']
            else: low,high=B['idx'],A['idx']
            for grp,sel in ((low,'max'),(high,'min')):
                cu=[(W@me.vertices[k].co).dot(u) for k in grp]; ext=max(cu) if sel=='max' else min(cu)
                for k,c in zip(grp,cu):
                    if abs(c-ext)<0.003:
                        w=W@me.vertices[k].co; w=w+u*(mid-c); z=dtm(w.x,w.y)
                        if z is not None: w.z=z+(0.42 if oh[k]>0.5 else -0.22)
                        me.vertices[k].co=Wi@w
            jp=W@me.vertices[low[0]].co; joints.append((ob.name,(u*mid+n*(A['nmin']+A['nmax'])/2).to_tuple(3),u.to_tuple(3),n.to_tuple(3)))
    me.update()
print('BUTT_JOINTS',npair,joints[:6])
# ---- (B)
om.use_fake_user=True
nm=om.copy(); nm.name=NM; nt=nm.node_tree; N=nt.nodes; L=nt.links.new
cm=N['EP_canopy_mix']; hz=N['EP_haze_mix']
at=N.new('ShaderNodeAttribute'); at.attribute_name='ou_edge'; at.attribute_type='GEOMETRY'
tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.035; nz.inputs['Detail'].default_value=4
nr_=N.new('ShaderNodeMapRange'); nr_.inputs['From Min'].default_value=0.35; nr_.inputs['From Max'].default_value=0.65; nr_.inputs['To Min'].default_value=0.72; nr_.inputs['To Max'].default_value=1.0
f=N.new('ShaderNodeMath'); f.operation='MULTIPLY'
mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; SI=lambda nd,i:[x for x in nd.inputs if x.identifier==i][0]; SI(mx,'B_Color').default_value=(0.40,0.49,0.32,1)
L(tc.outputs['Object'],nz.inputs['Vector']); L(nz.outputs['Fac'],nr_.inputs['Value'])
L(at.outputs['Fac'],f.inputs[0]); L(nr_.outputs['Result'],f.inputs[1]); L(f.outputs[0],mx.inputs['Factor'])
for l in list(nt.links):
    if l.from_node==cm and l.to_node==hz: src=l.from_socket; dst=l.to_socket; nt.links.remove(l)
L(src,SI(mx,'A_Color')); L([x for x in mx.outputs if x.identifier=='Result_Color'][0],dst)
for i,x in enumerate(sk.data.materials):
    if x and x.name==SM: sk.data.materials[i]=nm
g=bpy.data.node_groups.new(GN,'GeometryNodeTree')
g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=g.nodes; L=g.links.new
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=ter; oi.transform_space='RELATIVE'
px=N.new('GeometryNodeProximity')
mr=N.new('ShaderNodeMapRange'); mr.interpolation_type='SMOOTHSTEP'; mr.inputs['From Min'].default_value=2.0; mr.inputs['From Max'].default_value=150.0; mr.inputs['To Min'].default_value=1.0; mr.inputs['To Max'].default_value=0.0
st=N.new('GeometryNodeStoreNamedAttribute'); st.data_type='FLOAT'; st.domain='POINT'; st.inputs['Name'].default_value='ou_edge'
L(gi.outputs[0],st.inputs['Geometry']); L(st.outputs[0],go.inputs[0]); L(oi.outputs['Geometry'],px.inputs[0])
L(px.outputs['Distance'],mr.inputs['Value']); L(mr.outputs['Result'],st.inputs['Value'])
mo=sk.modifiers.new(GN,'NODES'); mo.node_group=g
sk['UNVERIFIED_ou']='ou: skirt tone darkened/greened within 150 m of the LiDAR DTM edge (GN OU_skirt_edge_tone + material copy); mesh unedited'
# ---- (C) cam on a joint near CELS
scn=bpy.context.scene; col=bpy.data.collections.new(CC); scn.collection.children.link(col)
cel=[j for j in joints if 'Environmental' in j[0]] or joints
dg=bpy.context.evaluated_depsgraph_get(); made=None
for jn,p,u,n in cel:
    p=Vector(p); n=Vector(n); 
    for sgn in (1,-1):
        z=dtm(p.x,p.y)
        if z is None: continue
        tgt=Vector((p.x,p.y,z+0.15)); loc=tgt+n*sgn*3.2+Vector(u)*0.8+Vector((0,0,0.95))
        h=scn.ray_cast(dg,loc,(tgt-loc).normalized(),distance=(tgt-loc).length+0.2)
        zl=dtm(loc.x,loc.y)
        if h[0] and (h[1]-tgt).length<0.25 and zl is not None and loc.z>zl+0.5:
            up=scn.ray_cast(dg,loc,Vector((0,0,1)),distance=30)
            if up[0]: continue
            made=(loc,tgt,jn); break
    if made: break
if made:
    d=bpy.data.cameras.new('OU_CAM_closeup_base_course_butt_joint'); d.lens=35; d.clip_end=6000
    o=bpy.data.objects.new(d.name,d); col.objects.link(o); o.location=made[0]; o.rotation_euler=(made[1]-made[0]).to_track_quat('-Z','Y').to_euler()
    print('CAM',made[2],made[0].to_tuple(2),made[1].to_tuple(2))
else: print('NO_CAM')
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
