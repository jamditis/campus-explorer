# ws126c: (b) leaf density 1700; burning bush smooth + vase/upright; pachysandra regenerated denser (0.075 m) and darker.
import bpy, bmesh, random, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
random.seed(1262)
sc=bpy.context.scene
col=bpy.data.collections['WS125_Chapin_W_bank_planting']
def minz(me): return min(v.co.z for v in me.vertices)
pts=[]; meshes=set()
for o in bpy.data.objects:
    if o.name.startswith(('WS125_bed_shrub_','WS126_bed_shrub_')):
        for m in o.modifiers:
            if m.type=='NODES' and 'Socket_2' in m.keys(): m['Socket_2']=1700.0
        if 'BurningBush' in o.name:
            base=o.location.z+minz(o.data)*o.scale.z
            o.scale=(o.scale.x*0.9,o.scale.y*0.9,o.scale.z*1.22); o.location.z=base-minz(o.data)*o.scale.z
            meshes.add(o.data)
        pts.append((o.location.x,o.location.y,0.45))
for me in meshes:
    for p in me.polygons: p.use_smooth=True
print('M126c bb meshes smoothed',len(meshes),'shrubs',len(pts))
# --- groundcover
old=[o for o in bpy.data.objects if o.name.startswith(('WS125_bed_groundcover_','WS126_Chapin_W_bank_pachysandra'))]
for o in old: bpy.data.objects.remove(o)
print('M126c removed old mounds',len(old))
mat=bpy.data.materials.get('WS126_Pachysandra_leaf_glossy') or bpy.data.materials.new('WS126_Pachysandra_leaf_glossy'); mat.use_nodes=True
nt=mat.node_tree; bsdf=nt.nodes['Principled BSDF']
bsdf.inputs['Roughness'].default_value=0.32
for n in list(nt.nodes):
    if n.type=='ATTRIBUTE': nt.nodes.remove(n)
at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='pcol'; at.attribute_type='GEOMETRY'
nt.links.new(at.outputs['Color'],bsdf.inputs['Base Color'])
me=bpy.data.meshes.new('WS126_pachysandra'); bm=bmesh.new()
cl=bm.loops.layers.color.new('pcol') if False else None
leafshape=[(0,0),(0.35,-0.42),(0.8,-0.5),(1.0,-0.2),(1.0,0.2),(0.8,0.5),(0.35,0.42)]  # obovate, broad toothed tip
nros=0; nl=0; faces_cols=[]
for bn in ('WS116_Chapin_W_bed_E1','WS116_Chapin_W_bed_E2','WS116_Chapin_W_bed_W'):
    bed=next(o for o in bpy.data.objects if o.name.startswith(bn))
    mw=bed.matrix_world; vs=[mw@v.co for v in bed.data.vertices]
    tree=BVHTree.FromPolygons(vs,[p.vertices for p in bed.data.polygons])
    # boundary edges (2D) for the clean mulch band
    ec={}
    for p in bed.data.polygons:
        for k in p.edge_keys: ec[k]=ec.get(k,0)+1
    bnd=[(vs[a].xy,vs[b].xy) for (a,b),c in ec.items() if c==1]
    def dseg(q):
        m=9
        for a,b in bnd:
            ab=b-a; t=max(0,min(1,(q-a).dot(ab)/max(ab.length_squared,1e-9))); m=min(m,(a+ab*t-q).length)
        return m
    xs=[v.x for v in vs]; ys=[v.y for v in vs]
    y=min(ys)
    while y<max(ys):
        x=min(xs)
        while x<max(xs):
            q=Vector((x+random.uniform(-0.035,0.035),y+random.uniform(-0.035,0.035)))
            loc,nor,idx,dist=tree.ray_cast(Vector((q.x,q.y,200)),Vector((0,0,-1)))
            if loc is not None and nor.z>0.4 and dseg(q)>0.30+random.uniform(-0.04,0.04) and all((q.x-a)**2+(q.y-b)**2>(r*0.85)**2 for a,b,r in pts):
                h=random.uniform(0.10,0.22); c=Vector((q.x,q.y,loc.z+h)); nros+=1
                L=random.uniform(0.065,0.095); W=L*0.42; rot0=random.uniform(0,6.28)
                g=random.uniform(0.85,1.15); colr=(0.022*g,0.065*g+random.uniform(-0.008,0.01),0.018*g,1)
                for j in range(6):
                    ang=rot0+j*math.tau/6+random.uniform(-0.2,0.2); tilt=math.radians(random.uniform(15,38))
                    ca,sa=math.cos(ang),math.sin(ang)
                    vv=[]
                    for u,w in leafshape:
                        lx=u*L*math.cos(tilt); lz=-u*L*math.sin(tilt)+0.012*u*(1-u)*4; ly=w*W
                        vv.append(bm.verts.new((c.x+lx*ca-ly*sa,c.y+lx*sa+ly*ca,c.z+lz)))
                    f=bm.faces.new(vv); faces_cols.append(colr); nl+=1
            x+=0.075
        y+=0.075
bm.to_mesh(me); bm.free()
ca=me.color_attributes.new('pcol','FLOAT_COLOR','CORNER')
li=0
for p,cc in zip(me.polygons,faces_cols):
    for l in p.loop_indices: ca.data[l].color=cc
me.materials.append(mat)
for p in me.polygons: p.use_smooth=False
gc=bpy.data.objects.new('WS126_Chapin_W_bank_pachysandra_carpet_rosettes_UNVERIFIEDspecies',me); col.objects.link(gc)
print('M126c pachysandra rosettes',nros,'leaves',nl,'faces',len(me.polygons))
bpy.ops.wm.save_mainfile(); print('M126c SAVED')
