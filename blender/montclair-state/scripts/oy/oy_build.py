# oy (UNVERIFIED, removable; REVERT=1 undoes): extend ox's 5-ft scoring-joint grid beyond the ox patch along more of the
# CELS/Calcia walks + per-panel tone variation, as LOCAL decal objects (shared walk material, OSM/terrain meshes untouched).
#  boxes: CELS_S (south of the ox box, OR view), CELS_W (walk north along x~115-121, close-up view), CALCIA (OQ view);
#  each box gets its own grid axis (dominant walk-edge direction mod 90), the walk patch is cut exactly at the box planes,
#  a straight expansion joint is drawn where a box plane crosses a walk, and the ox box gets tone only (its grid axis re-derived exactly like ox).
import bpy, os, sys, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OY_walk_joints_panel_tone_20261101oy_UNVERIFIED'; MATS=['OY_walk_joint_dark_UNVERIFIED','OY_walk_panel_tone_UNVERIFIED']
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0: (bpy.data.meshes if isinstance(d,bpy.types.Mesh) else bpy.data.cameras).remove(d)
    bpy.data.collections.remove(c)
for mn in MATS:
    m=bpy.data.materials.get(mn)
    if m and m.users==0: bpy.data.materials.remove(m)
if REV:
    print('REVERTED_OY')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
JS=1.524; JW=float(os.environ.get('JW','0.016')); TA=float(os.environ.get('TA','0.22'))
BOXES=[('CELS_S',118,145,183,201),('CELS_W',108,121,201,250),('CALCIA',-134,-102,193,228)]
OXB=(121,141,201,218)
F=bpy.data.objects['Footpaths_OSM']; dg=bpy.context.evaluated_depsgraph_get()
fe=F.evaluated_get(dg); me=fe.to_mesh(); full=bmesh.new(); full.from_mesh(me); full.transform(F.matrix_world); fe.to_mesh_clear()
def patch(x0,x1,y0,y1,exclude=None):
    b=full.copy()
    kill=[f for f in b.faces if not any(x0-3<=v.co.x<=x1+3 and y0-3<=v.co.y<=y1+3 for v in f.verts)]
    bmesh.ops.delete(b,geom=kill,context='FACES')
    for co,no in (((x0,0,0),(-1,0,0)),((x1,0,0),(1,0,0)),((0,y0,0),(0,-1,0)),((0,y1,0),(0,1,0))):
        bmesh.ops.bisect_plane(b,geom=b.verts[:]+b.edges[:]+b.faces[:],dist=1e-5,plane_co=Vector(co),plane_no=Vector(no),clear_outer=True)
    if exclude:
        ex0,ex1,ey0,ey1=exclude
        for co,no in (((ex0,0,0),(1,0,0)),((ex1,0,0),(-1,0,0)),((0,ey0,0),(0,1,0)),((0,ey1,0),(0,-1,0))): pass
        k=[f for f in b.faces if ex0<=f.calc_center_median().x<=ex1 and ey0<=f.calc_center_median().y<=ey1]
        bmesh.ops.delete(b,geom=k,context='FACES')
    b.verts.ensure_lookup_table(); return b
def on_plane(v,box): x0,x1,y0,y1=box; return min(abs(v.x-x0),abs(v.x-x1),abs(v.y-y0),abs(v.y-y1))<2e-3
def dom_axis(b,box):
    h={}
    for e in b.edges:
        if len(e.link_faces)!=1: continue
        a,c2=e.verts[0].co,e.verts[1].co
        if on_plane(a,box) and on_plane(c2,box): continue
        d=c2-a; L=math.hypot(d.x,d.y)
        if L<1e-3: continue
        k=int(round(math.degrees(math.atan2(d.y,d.x))%90))%90; h[k]=h.get(k,0)+L
    sm={k:sum(h.get((k+j)%90,0) for j in range(-3,4)) for k in range(90)}
    kb=max(sm,key=sm.get); num=sum(h.get((kb+j)%90,0)*(kb+j) for j in range(-3,4)); a=math.radians(num/sm[kb])
    return Vector((math.cos(a),math.sin(a),0))
def ox_axis():   # exact replica of ox's PCA (same evaluated mesh, same selection)
    X0,X1,Y0,Y1=OXB; b=full.copy()
    kill=[f for f in b.faces if not(X0-1<=f.calc_center_median().x<=X1+1 and Y0-1<=f.calc_center_median().y<=Y1+1)]
    bmesh.ops.delete(b,geom=kill,context='FACES')
    xs=[v.co for v in b.verts if X0<=v.co.x<=X1 and Y0<=v.co.y<=Y1]
    mx=sum(v.x for v in xs)/len(xs); my=sum(v.y for v in xs)/len(xs)
    sxx=sum((v.x-mx)**2 for v in xs); syy=sum((v.y-my)**2 for v in xs); sxy=sum((v.x-mx)*(v.y-my) for v in xs)
    b.free(); ang=0.5*math.atan2(2*sxy,sxx-syy); return Vector((math.cos(ang),math.sin(ang),0))
jt=bmesh.new(); tn=bmesh.new(); tl=tn.faces.layers.float.new('oy_tone'); nj=0; ns=0; info=[]
def hsh(i,j,s):
    h=(i*73856093)^(j*19349663)^(s*83492791); h&=0xffffffff; h=(h^(h>>13))*1274126177&0xffffffff; return ((h^(h>>16))&0xffff)/65535.0
def strip(a,b,w):
    global nj
    l=Vector((0,0,0.005)); vs=[jt.verts.new(x) for x in (a-w+l,b-w+l,b+w+l,a+w+l)]; jt.faces.new(vs); nj+=1
for si,(nm,x0,x1,y0,y1) in enumerate(BOXES+[('OX_TONE',)+OXB]):
    box=(x0,x1,y0,y1); b=patch(*box,exclude=OXB if nm!='OX_TONE' else None)
    if not b.faces: b.free(); continue
    ax=ox_axis() if nm=='OX_TONE' else dom_axis(b,box); ay=Vector((-ax.y,ax.x,0))
    bed=[e for e in b.edges if len(e.link_faces)==1 and not (on_plane(e.verts[0].co,box) and on_plane(e.verts[1].co,box))]
    ebvh=BVHTree.FromPolygons([e.verts[0].co.copy() for e in bed]+[e.verts[1].co.copy() for e in bed]+[e.verts[0].co+Vector((0,0,0.001)) for e in bed],[(i,i+len(bed),i+2*len(bed)) for i in range(len(bed))]) if bed else None
    def inside_edge(m): return not (ebvh and ebvh.find_nearest(m,0.06)[0] is not None)
    jb=b.copy()
    for axk in (ax,ay):
        pr=[axk.dot(Vector((v.co.x,v.co.y,0))) for v in jb.verts]
        for k in range(math.ceil(min(pr)/JS),math.floor(max(pr)/JS)+1):
            r=bmesh.ops.bisect_plane(jb,geom=jb.verts[:]+jb.edges[:]+jb.faces[:],dist=1e-5,plane_co=axk*(k*JS),plane_no=axk)
            if nm=='OX_TONE': continue
            for g in r['geom_cut']:
                if isinstance(g,bmesh.types.BMEdge) and len(g.link_faces)>=1:
                    a,c2=g.verts[0].co.copy(),g.verts[1].co.copy(); m=(a+c2)/2
                    if inside_edge(m): strip(a,c2,axk*(JW/2))
    # expansion joints where a box plane (incl. the ox box edge) cuts across the walk
    if nm!='OX_TONE':
        for e in b.edges:
            if len(e.link_faces)==1 and on_plane(e.verts[0].co,box) and on_plane(e.verts[1].co,box):
                a,c2=e.verts[0].co.copy(),e.verts[1].co.copy(); d=c2-a; d.z=0
                if d.length<1e-4: continue
                n=Vector((-d.y,d.x,0)).normalized(); m=(a+c2)/2
                if inside_edge(m): strip(a,c2,n*(JW*0.75)); ns+=1
    # per-panel tone overlay (3 mm over the walk, under the joints)
    vm={}
    for f in jb.faces:
        cc=f.calc_center_median(); i=math.floor(ax.dot(Vector((cc.x,cc.y,0)))/JS); j=math.floor(ay.dot(Vector((cc.x,cc.y,0)))/JS)
        vs=[]
        for v in f.verts:
            k=v.index
            if k not in vm: vm[k]=tn.verts.new(v.co+Vector((0,0,0.003)))
            vs.append(vm[k])
        try: nf=tn.faces.new(vs); nf[tl]=hsh(i,j,si+7)
        except ValueError: pass
    info.append((nm,round(math.degrees(math.atan2(ax.y,ax.x)),1),len(b.faces)))
    jb.free(); b.free()
full.free()
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
def mk(name,bmx,mat):
    mesh=bpy.data.meshes.new(name); bmx.to_mesh(mesh); bmx.free(); mesh.materials.append(mat)
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o['UNVERIFIED_oy']='no photo of these walks; 5-ft grid is the US default'; o.visible_shadow=False; return o
mj=bpy.data.materials.new(MATS[0]); mj.use_nodes=True; bb=mj.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value=(0.08,0.077,0.072,1); bb.inputs['Roughness'].default_value=0.95
mt=bpy.data.materials.new(MATS[1]); mt.use_nodes=True; nt=mt.node_tree; bb=nt.nodes['Principled BSDF']; out=nt.nodes['Material Output']; bb.inputs['Roughness'].default_value=0.9
at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='oy_tone'; at.attribute_type='GEOMETRY'
ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.30,0.285,0.26,1); ramp.color_ramp.elements[1].color=(0.80,0.79,0.76,1)
nt.links.new(at.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bb.inputs['Base Color'])
sub=nt.nodes.new('ShaderNodeMath'); sub.operation='SUBTRACT'; sub.inputs[1].default_value=0.5; nt.links.new(at.outputs['Fac'],sub.inputs[0])
ab=nt.nodes.new('ShaderNodeMath'); ab.operation='ABSOLUTE'; nt.links.new(sub.outputs[0],ab.inputs[0])
mu=nt.nodes.new('ShaderNodeMath'); mu.operation='MULTIPLY'; mu.inputs[1].default_value=TA*2; mu.use_clamp=True; nt.links.new(ab.outputs[0],mu.inputs[0])
tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeMixShader')
nt.links.new(mu.outputs[0],mx.inputs['Fac']); nt.links.new(tr.outputs[0],mx.inputs[1]); nt.links.new(bb.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],out.inputs['Surface'])
oj=mk('OY_walk_scoring_joints_CELS_Calcia_UNVERIFIED',jt,mj); ot=mk('OY_walk_panel_tone_CELS_Calcia_UNVERIFIED',tn,mt)
for p in ot.data.polygons: p.use_smooth=True
# close-up camera onto the Calcia walk junction (joints + panel tone)
FE2=F.evaluated_get(dg); FI=F.matrix_world.inverted()
def wz(x,y):
    ok,loc,n,i=FE2.ray_cast(FI@Vector((x,y,200)),(FI.to_3x3()@Vector((0,0,-1))).normalized())
    return (F.matrix_world@loc).z if ok else None
CX,CY,TX,TY=[float(v) for v in os.environ.get('OYCAM','-121.5,200.5,-114,207.5').split(',')]
cz=(wz(CX,CY) or wz(TX,TY)); tz=wz(TX,TY) or cz
cd=bpy.data.cameras.new('OY_CAM_closeup_calcia_walk_joints_panel_tone'); cd.lens=28
co=bpy.data.objects.new('OY_CAM_closeup_calcia_walk_joints_panel_tone',cd); col.objects.link(co)
co.location=Vector((CX,CY,cz+1.25)); co.rotation_euler=(Vector((TX,TY,tz))-co.location).to_track_quat('-Z','Y').to_euler()
print('OYCAM',tuple(round(x,2) for x in co.location),cz,tz)
print('OY boxes',info,'joint strips',nj,'expansion',ns,'tone faces',len(ot.data.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
