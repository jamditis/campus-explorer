src=open('/workspace/nj-scenes/montclair-state/scripts/ws234/probe234b.py').read().split("random.seed(1)")[0]
src=src.replace("m=o.data.copy(); m.transform(o.matrix_world)","dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); m=bpy.data.meshes.new_from_object(oe); m.transform(o.matrix_world); print('P235E eval',n,len(m.vertices),flush=True)")
import os
src=src.replace('M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam',os.environ.get('EXT','M3a_north_LiDAR_DTM_1m_ext_UNVERIFIED_seam'))
exec(src)
import collections
for n in ('Ballast 0 (Montclair Line)','Ballast 1 (Montclair Line)','MH Ballast rail_1','MH Ballast rail_2'):
    o=bpy.data.objects[n]; H=collections.defaultdict(list)
    for v in list(o.data.vertices)[::3]:
        w=o.matrix_world@v.co; g,gn=ground(w.x,w.y)
        if g is None: continue
        H[(int(w.y//50)*50, gn[:6])].append((w.z-g, round(w.x)))
    for k in sorted(H): 
        d=sorted(x[0] for x in H[k]); print('P235E',n[:12],k,len(d),'med',round(d[len(d)//2],2),'min',round(d[0],2),'x',min(x[1] for x in H[k]),max(x[1] for x in H[k]))
