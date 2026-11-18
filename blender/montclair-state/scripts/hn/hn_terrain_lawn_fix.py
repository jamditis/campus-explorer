# hn: terrain faces near the amphitheater still carried the 2020-construction ortho material (Ground_ortho_grass),
# showing as blocky dark/grey pixel patches next to the stage and a smeared olive slope above the top row.
# Reassign them to the post-2020 lawn (COLE_lawn_post2020_bs) inside a box around the amphitheater. Stores face ids for revert.
import bpy, json, os
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data; M=t.matrix_world
names=[s.material.name if s.material else '' for s in t.material_slots]
src=names.index('Ground_ortho_grass'); dst=names.index('COLE_lawn_post2020_bs')
BX=(-215,-138,-26,52)
if os.environ.get('REVERT')=='1' and 'hn_lawnfix' in t:
    for i in json.loads(t['hn_lawnfix']): me.polygons[i].material_index=src
    del t['hn_lawnfix']
else:
    ch=[]
    for p in me.polygons:
        if p.material_index!=src: continue
        c=M@p.center
        if BX[0]<=c.x<=BX[1] and BX[2]<=c.y<=BX[3]: p.material_index=dst; ch.append(p.index)
    old=json.loads(t.get('hn_lawnfix','[]')); t['hn_lawnfix']=json.dumps(sorted(set(old+ch)))
    print('HN LAWNFIX faces',len(ch))
me.update()
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('HN SAVED')
