"""ws17: the pale lens above Morehead's west eave (sign camera) = wide 'Eave_tile_top_soffit_under' top faces
lying in the west-slope plane. Reassign those top faces (slot 1, normal within 0.02 of the slope normal) to the
roof tile slot 0 so the tile field runs to the fascia. Also reverts the mhfix2 em_ringforce test (not saved).
APPLY=1 saves; otherwise renders a border crop."""
import bpy,bmesh,os
o=bpy.data.objects['Morehead Hall roof (LiDAR)']; me=o.data
N0=me.polygons[1029].normal.copy()
sel=[p.index for p in me.polygons if p.material_index==1 and (p.normal-N0).length<0.02]
A=sum(me.polygons[i].area for i in sel)
xs=[me.polygons[i].center for i in sel]
print('EAVETOP faces',len(sel),'area',round(A,2),'x',round(min(c.x for c in xs),1),round(max(c.x for c in xs),1),'y',round(min(c.y for c in xs),1),round(max(c.y for c in xs),1))
o['ws17_eavetop_to_tile']=str(sel)
for i in sel: me.polygons[i].material_index=0
me.update()
if os.environ.get('APPLY')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
else:
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws17/crop_render.py').read())
