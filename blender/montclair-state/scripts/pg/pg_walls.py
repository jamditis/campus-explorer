# pg (B): Feliciano walls double-up: the generic Wall_stucco_mission shader paints grey grid windows between the ported photo windows.
# Faces of 'Feliciano School of Business walls' that carry ported window objects get a plain-stucco copy (window/frame mix factors cut, bump cut).
# Shared material untouched. REVERT=1 restores face material indices and removes the slot/material. ALL UNVERIFIED.
import bpy,os,sys,json
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
w=bpy.data.objects['Feliciano School of Business walls']; me=w.data
MN='PG_Feliciano_wall_stucco_plain_no_shader_windows_UNVERIFIED'
if 'pg_prev_mi' in w:
    for i,mi in json.loads(w['pg_prev_mi']): me.polygons[i].material_index=mi
    del w['pg_prev_mi']
    idx=[k for k,s in enumerate(w.material_slots) if s.material and s.material.name==MN]
    for k in reversed(idx):
        w.active_material_index=k; me.materials.pop(index=k)
if MN in bpy.data.materials and bpy.data.materials[MN].users==0: bpy.data.materials.remove(bpy.data.materials[MN])
if not REV:
    base=bpy.data.materials['Wall_stucco_mission']; m=base.copy(); m.name=MN; nt=m.node_tree
    for l in list(nt.links):
        if (l.to_node.name in('Mix Shader','Mix Shader.001') and l.to_socket.name=='Fac') or l.to_node.name=='Bump' and l.to_socket.name=='Height':
            nt.links.remove(l)
    nt.nodes['Mix Shader'].inputs['Fac'].default_value=0.0; nt.nodes['Mix Shader.001'].inputs['Fac'].default_value=0.0
    me.materials.append(m); slot=len(me.materials)-1
    wins=[o for o in bpy.data.objects if o.name.startswith('Feliciano windows')]
    boxes=[]
    for o in wins:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        boxes.append((min(v.x for v in bb)-1.0,max(v.x for v in bb)+1.0,min(v.y for v in bb)-1.0,max(v.y for v in bb)+1.0,o.name))
    prev=[]
    for p in me.polygons:
        c=w.matrix_world@p.center
        if abs(p.normal.z)>0.3: continue
        if any(b[0]<c.x<b[1] and b[2]<c.y<b[3] for b in boxes):
            prev.append((p.index,p.material_index)); p.material_index=slot
    w['pg_prev_mi']=json.dumps(prev); w['UNVERIFIED_pg_walls']='plain stucco where photo windows were ported'
    print('PG_WALLS faces',len(prev),[x[0] for x in prev])
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PG_WALLS_DONE',REV)
