# ws149 data prep (memory-safe partial scene): which tree INSTANCES hang leaf cards < 2.4 m above PAVING (walks/drives/lots)?
# Output feeds a per-instance crown-raise pass (make the mesh single-user for those instances only).
import bpy, bmesh, json, resource
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
idx=[json.loads(l) for l in open('/workspace/nj-scenes/montclair-state/scripts/ws147/bboxes.jsonl')]
pave=[d['n'] for d in idx if d['t']=='MESH' and not d['n'].startswith('T_') and any(k in m.lower() for m in d['mats'] for k in ('concrete','asphalt','brick','paver','walk')) and not any(k in d['n'].lower() for k in ('curb','wall','stair','step','build','hall','roof','facade','window','wing','tower','pier','column','arcade','bench','plinth','base','terrain','dtm','ground','patch','lawn','skirt','drape','ortho_','fill','bank','bed'))]
trees=[d['n'] for d in idx if d['n'].startswith('T_')]
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=trees+pave
print("LOADED",len(trees),len(pave),"RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
V=[];F=[]
for o in dst.objects:
    if o is None or o.name.startswith('T_') or o.type!='MESH': continue
    me=o.data; mw=o.matrix_basis if o.parent is None else (o.parent.matrix_basis@o.matrix_parent_inverse@o.matrix_basis); b=len(V)
    V+= [mw@v.co for v in me.vertices]; F+=[[b+i for i in p.vertices] for p in me.polygons]
T=BVHTree.FromPolygons(V,F); print("PAVE faces",len(F)); [print("PAVEOBJ",o.name,len(o.data.polygons)) for o in dst.objects if o and not o.name.startswith("T_") and o.type=="MESH" and len(o.data.polygons)>20000]
cache={}
out=[]
for o in dst.objects:
    if o is None or not o.name.startswith('T_') or o.type!='MESH': continue
    me=o.data
    if me.name not in cache:
        leaf={i for i,m in enumerate(me.materials) if m and 'Leaf' in m.name}
        cache[me.name]=[p.center.copy() for p in me.polygons if p.material_index in leaf]
    mw=o.matrix_basis if o.parent is None else (o.parent.matrix_basis@o.matrix_parent_inverse@o.matrix_basis); n=0; hit=0; minc=99
    for c in cache[me.name]:
        w=mw@c
        h=T.ray_cast(Vector((w.x,w.y,w.z-0.02)),Vector((0,0,-1)),6.0)
        if h[0] is None: continue
        clr=w.z-h[0].z
        if 0.0<clr<2.4: hit+=1; minc=min(minc,clr)
    if hit: out.append((o.name,me.name,hit,round(minc,2),[round(x,1) for x in mw.translation]))
out.sort(key=lambda r:-r[2])
for r in out: print("LOWOVERPAVE",*r)
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws149/treepave149.json','w'))
print("N",len(out),"RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
