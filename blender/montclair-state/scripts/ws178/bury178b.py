import bpy, numpy as np, os, re
from mathutils.bvhtree import BVHTree
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PRE=('WS138b_ground_fill','WS134_ground_patch','WS133b_ground_patch','WS163','WS110','WS172','WS173','WS174','WS175','WS166','WS170','WS113_paving_tops_proxy','UTIL170')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE) and 'skirt' not in n.lower() and 'CAM' not in n and 'hidden' not in n]
sc=bpy.context.scene
for o in b.objects:
    if o and o.name not in sc.collection.objects: sc.collection.objects.link(o)
if os.environ.get('FIX')=='1':
    for f in ('fix177.py','fix177b.py','fix177c.py'): exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/'+f).read())
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws178/fix178.py').read())
dg=bpy.context.evaluated_depsgraph_get()
objs=[o for o in b.objects if o and o.type=='MESH']
pav=[o for o in objs if re.search(r'carriageway|curb|kerb|sidewalk|walk|road|drive|apron|concrete|asphalt|paving|crosswalk',o.name,re.I) and 'proxy' not in o.name and not re.search(r'ground|lawn|grass|verge',o.name,re.I)]
gnd=[o for o in objs if re.search(r'ground|lawn|patch|fill|grass|yard|bank',o.name,re.I) and o not in pav]
print('PAV',len(pav),'GND',len(gnd),flush=True)
trees=[(o,BVHTree.FromObject(o,dg)) for o in pav]
for g in gnd:
    ge=g.evaluated_get(dg); me=ge.to_mesh(); M=g.matrix_world
    W=np.array([(M@v.co)[:] for v in me.vertices]); ge.to_mesh_clear()
    bad=[]
    for w in W:
        for o,tr in trees:
            Mi=o.matrix_world.inverted(); pl=Mi@Vector((w[0],w[1],w[2]+30)); dl=(Mi.to_3x3()@Vector((0,0,-1))).normalized()
            hit=tr.ray_cast(pl,dl,80)
            if hit[0] is not None:
                hz=(o.matrix_world@hit[0]).z
                if w[2]>hz+0.005 and w[2]-hz<1.5: bad.append((w[0],w[1],w[2]-hz,o.name[:28]))
                break
    if bad:
        B=np.array([[x,y,d] for x,y,d,_ in bad]); names=sorted(set(n for *_,n in bad))
        print('BURY',g.name[:34],len(bad),'max',round(B[:,2].max(),3),'x',round(B[:,0].min(),1),round(B[:,0].max(),1),'y',round(B[:,1].min(),1),round(B[:,1].max(),1),names[:4],flush=True)
        # cluster in 10 m bins
        bins={}
        for x,y,dz in B: k=(int(x//10)*10,int(y//10)*10); bins[k]=max(bins.get(k,0),dz)
        print('  BINS',sorted([(k,round(v,2)) for k,v in bins.items() if v>0.03],key=lambda z:-z[1])[:12],flush=True)
    else: print('OK',g.name[:34],len(W),flush=True)
print('DONE',flush=True)
