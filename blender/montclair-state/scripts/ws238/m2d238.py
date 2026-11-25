# ws238 ONE-SCENE M2 batch (d): north lamp posts (North_lamp_posts, 105 candidates from scripts/ws236/m2d_nlamp_candidates236.json)
# into main under NORTH_MERGE/N_lamps. Rule (same as M3a/M3b terrain): only lamps standing on NORTH-NATIVE ground (first ground hit
# straight down = M3a/M3b north 1 m LiDAR DTM) come in; lamps over main-native ground are skipped (main has its own lamps there).
# Also skipped: any lamp within 4 m (XY) of an existing main lamp. Kept lamps are seated: bbox min z -> ground (base meshes;
# M3a/M3b carry no modifiers). |dz| > 0.2 m -> skipped as UNVERIFIED. University Hall untouched (script refuses UH*).
import bpy, json, mathutils
from mathutils.kdtree import KDTree
MS='/workspace/nj-scenes/montclair-state/'
NORTH=MS+'north/montclair_north.blend'
cand=json.load(open(MS+'scripts/ws236/m2d_nlamp_candidates236.json'))
want=[n for n in cand if n not in bpy.data.objects and not n.startswith(('UH','University Hall'))]
sc=bpy.context.scene
def coll(name,parent):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in parent.children]: parent.children.link(c)
    return c
NM=coll('NORTH_MERGE',sc.collection); NL=coll('N_lamps',NM)
# existing main lamps (XY of bbox centre)
ex=[]
for o in bpy.data.objects:
    if o.type in ('MESH','EMPTY') and 'lamp' in o.name.lower() and o.name not in cand:
        if o.type=='MESH':
            c=sum((o.matrix_world@mathutils.Vector(b) for b in o.bound_box),mathutils.Vector())/8
        else: c=o.matrix_world.translation
        ex.append(c)
kd=KDTree(max(1,len(ex)))
for i,c in enumerate(ex): kd.insert((c.x,c.y,0),i)
kd.balance()
print('M2D want',len(want),'main lamps',len(ex),flush=True)
before=set(bpy.data.objects)
with bpy.data.libraries.load(NORTH,link=False) as (src,dst):
    have=set(src.objects); dst.objects=[n for n in want if n in have]
app=[o for o in dst.objects if o]
for o in app: NL.objects.link(o)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
appset=set(o.name for o in app)
def ground(x,y,ztop):
    org=mathutils.Vector((x,y,ztop)); d=mathutils.Vector((0,0,-1))
    for _ in range(40):
        hit,loc,nrm,idx,ob,mat=sc.ray_cast(dg,org,d)
        if not hit: return None,None
        n=ob.name
        if n in appset or 'lamp' in n.lower() or n.startswith(('T_','Tree','NT_')) or ob.type!='MESH' or nrm.z<0.3:
            org=loc+d*0.01; continue
        return loc.z,n
    return None,None
keep=[];rep=[]
for o in app:
    bb=[o.matrix_world@mathutils.Vector(b) for b in o.bound_box]
    c=sum(bb,mathutils.Vector())/8; zmin=min(v.z for v in bb)
    _,_,dn=kd.find((c.x,c.y,0)) if ex else (None,None,1e9)
    gz,gn=ground(c.x,c.y,zmin+60)
    why=None
    if dn<4.0: why='dup %.1fm'%dn
    elif gz is None: why='noground'
    elif not gn.startswith(('M3a_','M3b_')): why='main-native '+gn[:40]
    elif abs(gz-zmin)>0.2: why='dz %.2f UNVERIFIED'%(gz-zmin)
    rep.append((o.name,round(c.x,1),round(c.y,1),gn and gn[:30],None if gz is None else round(gz-zmin,3),why))
    if why: bpy.data.objects.remove(o,do_unlink=True)
    else:
        o.location.z+=gz-zmin; keep.append(o.name)
from collections import Counter
print('M2D kept',len(keep),'skipped',Counter((r[5] or 'keep').split(' ')[0] for r in rep),flush=True)
print('M2D dz kept',sorted(r[4] for r in rep if not r[5])[:3],sorted(r[4] for r in rep if not r[5])[-3:],flush=True)
for L in list(bpy.data.libraries):
    if L.filepath.endswith('north/montclair_north.blend'):
        users=[i for t in ('objects','meshes','materials','images','node_groups') for i in getattr(bpy.data,t) if i.library==L]
        if not users: bpy.data.libraries.remove(L); print('M2D north lib removed',flush=True)
new=[o.name for o in bpy.data.objects if o not in before]
print('M2D new objects',len(new),'N_lamps',len(NL.objects),flush=True)
json.dump(rep,open(MS+'scripts/ws238/m2d_report238.json','w'),indent=0)
