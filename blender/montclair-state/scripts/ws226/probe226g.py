import os,json
os.environ['DRY']='1'
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws226/fix226a.py').read())
B,_=terrain_bvh()
g=[]
for x in range(-240,250,10):
    for y in range(-240,250,10):
        z=top(B,x+.5,y+.5); g.append((x,y,float(A[int(y+250),int(x+250)]),z))
json.dump(g,open('/workspace/nj-scenes/montclair-state/scripts/ws226/probe226g_grid.json','w'))
# which base faces lie over the remaining high cells
me=t.data
BB=BVHTree.FromPolygons([v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
seen={}
for x,y,d,z in g:
    if z is not None and z-d>2:
        h=BB.ray_cast(Vector((x+.5,y+.5,400)),Vector((0,0,-1)))
        if h[0] is not None: seen.setdefault(h[2],[]).append((x,y,round(z-d,1),round(h[0].z-d,1)))
for k,v in sorted(seen.items(),key=lambda kv:-len(kv[1]))[:12]:
    p=me.polygons[k]; print('P226G face',k,round(p.area),len(p.vertices),tuple(round(c) for c in p.center[:2]),len(v),v[:4],flush=True)
import sys; sys.stdout.flush(); os._exit(0)
