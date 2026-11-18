import bpy, json
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
rep={}
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
trees=[o for o in bpy.data.objects if o.name.startswith('WQ_south_wood_tree_')]
hits={}
for o in trees:
    x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
    for dx,dy in [(3,0),(-3,0),(0,3),(0,-3)]:
        org=Vector((x+dx,y+dy,400)); 
        ok,loc,nrm,idx,ob,mx=sc.ray_cast(dg,org,Vector((0,0,-1)))
        # skip tree hits
        while ok and (ob.name.startswith(('WQ_','WM_south','T_','WJ_')) or 'tree' in ob.name.lower()):
            ok,loc,nrm,idx,ob,mx=sc.ray_cast(dg,loc-Vector((0,0,0.01)),Vector((0,0,-1)))
        if ok:
            ev=ob.evaluated_get(dg); me=ev.data
            try: mat=ev.material_slots[me.polygons[idx].material_index].material.name
            except Exception as e: mat=str(e)
            k=(ob.name,mat); hits[str(k)]=hits.get(str(k),0)+1
rep['hits']=hits
rep['trees_xy']=[(round(o.matrix_world.translation.x,1),round(o.matrix_world.translation.y,1)) for o in trees]
def dump(mn):
    m=bpy.data.materials.get(mn)
    if not m: return None
    return {'users':m.users,'nodes':[(n.name,n.bl_idname) for n in m.node_tree.nodes],
     'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]}
mats=set(eval(k)[1] for k in hits)
rep['mats']={mn:dump(mn) for mn in mats}
# who uses those mats
for mn in mats:
    rep.setdefault('mat_objs',{})[mn]=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material and s.material.name==mn for s in o.material_slots)][:20]
rep['WH']=dump('WH_east_dorm_patch_tone_UNVERIFIED')
im=bpy.data.images.get('WM_litter_mask'); rep['img']=list(im.size) if im else None
json.dump(rep,open(R+'/data/wr/probe.json','w'),indent=1)
print('HITS',hits)
