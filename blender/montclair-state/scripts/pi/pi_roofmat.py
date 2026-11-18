# pi: Feliciano LiDAR roof faces carrying Wall_stucco_mission (slot 3).
# (A) sloped ones (0.3<|nz|<0.95, white hip shards from the air) -> slot 0 Roof_tile_or_membrane.
# (B) vertical ones (LiDAR step walls; the shared shader paints grey grid windows on them -> grey slivers above the pavilion)
#     -> plain-stucco copy made in pg (PG_Feliciano_wall_stucco_plain_no_shader_windows_UNVERIFIED), appended as a new slot.
# REVERT=1 restores indices and removes the slot. ALL UNVERIFIED.
import bpy,os,sys,json
REV=os.environ.get('REVERT')=='1'
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; me=r.data; R=r.matrix_world.to_3x3()
MN='PG_Feliciano_wall_stucco_plain_no_shader_windows_UNVERIFIED'
if 'pi_prev_mi' in r:
    for i,mi in json.loads(r['pi_prev_mi']): me.polygons[i].material_index=mi
    del r['pi_prev_mi']
    idx=[k for k,s in enumerate(r.material_slots) if s.material and s.material.name==MN]
    for k in reversed(idx): me.materials.pop(index=k)
    if 'UNVERIFIED_pi_roofmat' in r: del r['UNVERIFIED_pi_roofmat']
if not REV:
    me.materials.append(bpy.data.materials[MN]); slot=len(me.materials)-1
    prev=[];a=b=0
    for p in me.polygons:
        if p.material_index!=3: continue
        nz=abs((R@p.normal).normalized().z)
        if 0.3<nz<0.95: prev.append((p.index,3)); p.material_index=0; a+=1
        elif nz<=0.3: prev.append((p.index,3)); p.material_index=slot; b+=1
    r['pi_prev_mi']=json.dumps(prev); r['UNVERIFIED_pi_roofmat']='LiDAR roof hips -> tile, step walls -> plain stucco'
    print('PI_ROOFMAT tile',a,'plain',b)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PI_DONE',REV)
