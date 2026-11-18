# oj signature for the revert test: object/collection counts, hide flags, Schmitt mesh hashes, material node/link counts + key values.
import bpy, hashlib, json, sys
def mh(me):
    h=hashlib.sha1()
    for v in me.vertices: h.update(('%.4f,%.4f,%.4f;'%tuple(v.co)).encode())
    for p in me.polygons: h.update((','.join(map(str,p.vertices))+'|%d;'%p.material_index).encode())
    return h.hexdigest()[:16]
out={'n_obj':len(bpy.data.objects),'n_scene':len(bpy.context.scene.objects),'n_col':len(bpy.data.collections),'n_mat':len(bpy.data.materials),'n_mesh':len(bpy.data.meshes)}
for n in ['OI_Schmitt_pavilion_shell_stucco','OI_Schmitt_lettering_CONRAD_J_SCHMITT_HALL','Schmitt Hall walls','Schmitt Hall roof (LiDAR)','Footpaths_OSM']:
    o=bpy.data.objects[n]; out['mesh:'+n]=mh(o.data); out['mat:'+n]=[m.name if m else None for m in o.data.materials]
for n in ['OI_Schmitt_pavilion_arch_glass','OI_Schmitt_pavilion_top_window_glass']: out['mat:'+n]=[m.name for m in bpy.data.objects[n].data.materials]
for mn in ['OH_Schmitt_stucco_block_base_UNVERIFIED','OI_Schmitt_pier_block_plinth_UNVERIFIED','OI_Schmitt_pavilion_roof_tile_UNVERIFIED','OH_Schmitt_door_glass_clear_UNVERIFIED']:
    nt=bpy.data.materials[mn].node_tree; d={'nodes':len(nt.nodes),'links':len(nt.links)}
    for n in nt.nodes:
        if n.type in('TEX_BRICK','BSDF_PRINCIPLED'):
            for s in n.inputs:
                if s.name in('Color1','Color2','Mortar','Bias','Base Color','Roughness'): d[n.name+'|'+s.name]=[round(x,4) for x in s.default_value] if hasattr(s.default_value,'__len__') else round(s.default_value,4); d[n.name+'|'+s.name+'|L']=s.is_linked
    out['mt:'+mn]=d
h=hashlib.sha1()
for o in sorted(bpy.data.objects,key=lambda o:o.name): h.update(('%s%d%d%s'%(o.name,o.hide_render,o.hide_viewport,[round(x,3) for x in o.matrix_world.translation])).encode())
out['hide_xform']=h.hexdigest()[:16]
json.dump(out,open(sys.argv[sys.argv.index('--')+1],'w'),indent=1,sort_keys=True); print('SIG',out['n_obj'],out['n_scene'])
