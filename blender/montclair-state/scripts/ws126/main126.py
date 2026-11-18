# ws126: Chapin W entrance banks — shrubs -15% + prune/shape variety (BurningBush, upright yews, irregular/tilted),
# groundcover mounds -> real pachysandra rosette carpet (whorls of 6 obovate leaves), clean 0.3 m mulch edge band.
import bpy, bmesh, random, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
random.seed(126)
sc=bpy.context.scene
col=bpy.data.collections['WS125_Chapin_W_bank_planting']
LIB='/workspace/nj-scenes/assets/campus_assets.blend'
with bpy.data.libraries.load(LIB,link=False) as (df,dt):
    dt.objects=['Shrub_BurningBush','ShrubLeaf_BurningBush']
bb_src=next(o for o in dt.objects if o.name.startswith('Shrub_BurningBush'))
leaf=next(o for o in dt.objects if o.name.startswith('ShrubLeaf_BurningBush'))
col.objects.link(leaf); leaf.hide_render=True; leaf.hide_viewport=True
def minz(me): return min(v.co.z for v in me.vertices)
shr=sorted([o for o in bpy.data.objects if o.name.startswith('WS125_bed_shrub_')],key=lambda o:o.name)
pts=[]; forms={}
for i,o in enumerate(shr):
    base=o.location.z+minz(o.data)*o.scale.z
    sx,sy,sz=[s*0.85 for s in o.scale]
    r=random.random()
    if i%5==2:   # burning bush (Euonymus alatus 'Compactus'), vase/upright
        n=bb_src.copy(); n.data=bb_src.data; col.objects.link(n)
        n.name=o.name.replace('WS125_bed_shrub_','WS126_bed_shrub_').split('_UNVERIFIED')[0].rsplit('_',1)[0]+'_BurningBush_UNVERIFIEDspecies'
        d=bb_src.dimensions; w=random.uniform(0.8,1.0); h=random.uniform(0.85,1.05)
        n.scale=(w/max(d.x,d.y),w/max(d.x,d.y)*random.uniform(0.9,1.1),h/d.z)
        n.rotation_euler=(0,0,random.uniform(0,6.28))
        n.location=(o.location.x,o.location.y,base-0.03-minz(n.data)*n.scale.z)
        pts.append((o.location.x,o.location.y,w*0.5)); forms['burningbush']=forms.get('burningbush',0)+1
        bpy.data.objects.remove(o); continue
    if 'Yew' in o.name and r<0.6:   # upright pruned yew
        sx*=0.8; sy*=0.8; sz*=1.22; f='upright'
    elif r<0.5:                       # irregular, informally pruned
        a=random.uniform(1.12,1.28); sx*=a; sy/=a**0.6; sz*=random.uniform(0.85,1.0); f='irregular'
        o.rotation_euler[0]=math.radians(random.uniform(-6,6)); o.rotation_euler[1]=math.radians(random.uniform(-6,6))
    else:
        s=random.uniform(0.9,1.05); sx*=s; sy*=s; sz*=random.uniform(0.8,1.05); f='round'
    o.scale=(sx,sy,sz)
    o.location.z=base-0.02-minz(o.data)*sz
    forms[f]=forms.get(f,0)+1
    pts.append((o.location.x,o.location.y,0.5*min(sx,sy)*max(o.data.dimensions.x,o.data.dimensions.y) if hasattr(o.data,'dimensions') else 0.45))
print('M126 shrub forms',forms)
# fix radius list (mesh has no dimensions attr): use object dims
pts=[(p[0],p[1],0.42) if p[2]<=0.0 else p for p in pts]
# --- groundcover
old=[o for o in bpy.data.objects if o.name.startswith('WS125_bed_groundcover_')]
for o in old: bpy.data.objects.remove(o)
print('M126 removed old mounds',len(old))
mat=bpy.data.materials.new('WS126_Pachysandra_leaf_glossy'); mat.use_nodes=True
nt=mat.node_tree; bsdf=nt.nodes['Principled BSDF']
bsdf.inputs['Roughness'].default_value=0.38
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
            q=Vector((x+random.uniform(-0.045,0.045),y+random.uniform(-0.045,0.045)))
            loc,nor,idx,dist=tree.ray_cast(Vector((q.x,q.y,200)),Vector((0,0,-1)))
            if loc is not None and nor.z>0.4 and dseg(q)>0.30+random.uniform(-0.04,0.04) and all((q.x-a)**2+(q.y-b)**2>(r*0.85)**2 for a,b,r in pts):
                h=random.uniform(0.13,0.22); c=Vector((q.x,q.y,loc.z+h)); nros+=1
                L=random.uniform(0.065,0.095); W=L*0.42; rot0=random.uniform(0,6.28)
                g=random.uniform(0.85,1.15); colr=(0.045*g,0.12*g+random.uniform(-0.01,0.015),0.03*g,1)
                for j in range(6):
                    ang=rot0+j*math.tau/6+random.uniform(-0.2,0.2); tilt=math.radians(random.uniform(15,38))
                    ca,sa=math.cos(ang),math.sin(ang)
                    vv=[]
                    for u,w in leafshape:
                        lx=u*L*math.cos(tilt); lz=-u*L*math.sin(tilt)+0.012*u*(1-u)*4; ly=w*W
                        vv.append(bm.verts.new((c.x+lx*ca-ly*sa,c.y+lx*sa+ly*ca,c.z+lz)))
                    f=bm.faces.new(vv); faces_cols.append(colr); nl+=1
            x+=0.10
        y+=0.10
bm.to_mesh(me); bm.free()
ca=me.color_attributes.new('pcol','FLOAT_COLOR','CORNER')
li=0
for p,cc in zip(me.polygons,faces_cols):
    for l in p.loop_indices: ca.data[l].color=cc
me.materials.append(mat)
for p in me.polygons: p.use_smooth=False
gc=bpy.data.objects.new('WS126_Chapin_W_bank_pachysandra_carpet_rosettes_UNVERIFIEDspecies',me); col.objects.link(gc)
print('M126 pachysandra rosettes',nros,'leaves',nl,'faces',len(me.polygons))
bpy.ops.wm.save_mainfile(); print('M126 SAVED')
