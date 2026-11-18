import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(M,link=False) as (src,dst):
    want=[n for n in src.objects if n.startswith(('WS75_sprague','WS80_sprague','WS68_RHD_ground','WS81_','WS76_','WS79_lot')) or n=='Terrain_LiDAR_DTM_1m']
    dst.objects=want
sc=bpy.context.scene
for o in dst.objects:
    if o: sc.collection.objects.link(o)
print('LOADED',[(o.name,o.type,len(o.data.polygons) if o.type=='MESH' else 0,[m.name for m in o.data.materials] if o.type=='MESH' else [], [md.type for md in o.modifiers]) for o in dst.objects if o],flush=True)
def dump(mn):
    m=bpy.data.materials.get(mn)
    if not m or not m.node_tree: print('NOMAT',mn); return
    print('MAT',mn)
    for n in m.node_tree.nodes:
        ex=''
        if n.type=='TEX_IMAGE' and n.image: ex=n.image.filepath
        if n.type=='VALTORGB': ex=[(round(e.position,3),tuple(round(c,2) for c in e.color)) for e in n.color_ramp.elements]
        if n.type=='MATH': ex=(n.operation,[round(i.default_value,3) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')])
        if n.type=='MAPPING': ex=[tuple(round(v,3) for v in n.inputs[k].default_value) for k in ('Location','Scale')]
        print('  N',n.name,n.type,n.label,ex)
    for l in m.node_tree.links: print('  L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
mats=set()
for o in dst.objects:
    if o and o.type=='MESH':
        for m in o.data.materials:
            if m: mats.add(m.name)
for mn in sorted(mats):
    if 'Lawn' in mn or 'ortho' in mn.lower() or 'grass' in mn.lower(): dump(mn)
# UV of WS75
o=bpy.data.objects.get('WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges')
uv=o.data.uv_layers.active
for li in range(0,40,13):
    lp=o.data.loops[li]; v=o.matrix_world@o.data.vertices[lp.vertex_index].co; print('UV75',tuple(round(c,3) for c in v),tuple(round(c,4) for c in uv.data[li].uv))
# terrain face materials in the streak area + ray probes along the eye-S camera
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def gz(x,y):
    ok,loc,*_=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1))); return loc.z if ok else 125
def mkcam(name,eye,tgt,lens):
    c=bpy.data.cameras.new(name); c.lens=lens; ob=bpy.data.objects.new(name,c)
    d=Vector(tgt)-Vector(eye); ob.location=eye; ob.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); return ob
sc.render.resolution_x=704; sc.render.resolution_y=396
specs={'EYES':((-227,-134,0),(-229,-96),28,1.7,0.5,[(20,268),(60,264),(100,259),(140,254),(180,249),(220,244),(60,258),(100,253),(140,248),(30,272),(250,240)]),
       'OBL':((-290,-165,175),(-245,-108),30,None,0.0,[(465,200),(460,220),(455,245),(450,265),(447,285),(470,205),(458,230),(452,255)])}
for k,(e,t,lens,h,th,pxs) in specs.items():
    ez=e[2] if h is None else gz(e[0],e[1])+h; tz=gz(t[0],t[1])+th
    c=mkcam('P_'+k,(e[0],e[1],ez),(t[0],t[1],tz),lens); sc.collection.objects.link(c); bpy.context.view_layer.update()
    TR,BR,BL,TL=[c.matrix_world@v for v in c.data.view_frame(scene=sc)]; o0=c.matrix_world.translation
    for px,py in pxs:
        u=px/704; v=py/396; p=(TL.lerp(TR,u)).lerp(BL.lerp(BR,u),v); d=(p-o0).normalized(); org=o0.copy(); hits=[]
        for _ in range(3):
            ok,loc,n,i,ob,m=sc.ray_cast(dg,org,d)
            if not ok: hits.append('MISS'); break
            try: mat=ob.material_slots[ob.data.polygons[i].material_index].material.name
            except Exception: mat=None
            hits.append((ob.name[:30],i,mat,tuple(round(x,2) for x in loc),round(n.z,2))); org=loc+d*0.01
        print('PX',k,px,py,hits,flush=True)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws82/lite82.blend')
print('DONE')
