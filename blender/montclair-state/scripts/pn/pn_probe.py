import bpy, numpy as np
for o in bpy.data.objects:
    if 'eliciano' in o.name and o.type=='MESH':
        me=o.data; mw=o.matrix_world
        co=np.array([tuple(mw@v.co) for v in me.vertices]) if len(me.vertices) else np.zeros((1,3))
        print('OBJ',repr(o.name),len(me.vertices),len(me.polygons),'hide',o.hide_render,'x',co[:,0].min().round(1),co[:,0].max().round(1),'y',co[:,1].min().round(1),co[:,1].max().round(1),'z',co[:,2].min().round(1),co[:,2].max().round(1),[m.name for m in me.materials][:8] if me.materials else '')
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; me=r.data; mw=r.matrix_world
zs=[];
for p in me.polygons:
    if p.normal.z>0.9: zs.append(round((mw@p.center).z,0))
import collections; print('FLATZ',sorted(collections.Counter(zs).items()))
