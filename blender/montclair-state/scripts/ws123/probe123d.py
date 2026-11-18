import bpy
e=bpy.data.objects.get('WS123_Chapin_W_planter_tree_HoneyLocust_young_UNVERIFIEDspecies')
print('E',e and (tuple(e.location),e.hide_render,[c.name for c in e.users_collection],e.instance_collection and e.instance_collection.name, e.instance_collection and e.instance_collection.library and e.instance_collection.library.filepath))
c=bpy.data.collections.get('Tree_HoneyLocust_LOD1_Oct_turning'); print('C',c and [(o.name,o.type,len(o.data.polygons) if o.type=='MESH' else 0) for o in c.all_objects], c and c.library and c.library.filepath)
for col in e.users_collection:
    def find(lc):
        if lc.collection==col: return lc
        for ch in lc.children:
            r=find(ch)
            if r: return r
    lc=find(bpy.context.view_layer.layer_collection); print('LC',lc and (lc.exclude,lc.hide_viewport,col.hide_render))
