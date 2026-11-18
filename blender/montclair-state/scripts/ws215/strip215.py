# Release copy: make linked data local, drop ortho/aerial/LiDAR-raster images, pack own + CC0 textures, save compressed.
import bpy, re, json, os
OUT=os.environ['OUT']
PAT=re.compile(r'ortho|naip|aerial|/refs/|lidar|dtm|dem_|3dep|hillshade|_he\.exr|/he/', re.I)
for im in bpy.data.images:
    if im.library and im.filepath:
        im_abs=bpy.path.abspath(im.filepath, library=im.library)
        try: im.filepath=im_abs
        except Exception: pass
COLLS=[getattr(bpy.data,a) for a in ('objects','meshes','materials','node_groups','images','collections','curves','textures','worlds','lights','cameras','actions','grease_pencils','lattices','metaballs','fonts','particles','palettes','brushes','scenes','texts','volumes','pointclouds','hair_curves','armatures','shape_keys') if hasattr(bpy.data,a)]
for _ in range(12):
    n=0
    for coll in COLLS:
        for idb in list(coll):
            if idb.library:
                try: idb.make_local(); n+=1
                except Exception as e: print('ML fail',idb.name,e)
    print('made local',n)
    if n==0: break
strip=[im for im in bpy.data.images if PAT.search(im.filepath or '') or PAT.search(im.name)]
names={im.name for im in strip}
rep=[]
def fix_tree(tree,owner):
    for nd in list(tree.nodes):
        if nd.bl_idname=='ShaderNodeTexImage' and nd.image and nd.image.name in names:
            rep.append((owner,nd.image.name,'shader'))
            rgb=tree.nodes.new('ShaderNodeRGB'); rgb.location=nd.location
            mn=owner.lower()
            col=(0.085,0.085,0.083,1) if any(k in mn for k in ('asphalt','lot','road','plinth','paint')) else ((0.11,0.19,0.065,1) if any(k in mn for k in ('grass','lawn','ground','skirt','farfield','haze')) else (0.2,0.2,0.18,1))
            rgb.outputs[0].default_value=col
            for l in list(nd.outputs['Color'].links): tree.links.new(rgb.outputs[0], l.to_socket)
            nd.image=None
        elif nd.bl_idname=='GeometryNodeImageTexture' or (nd.bl_idname=='GeometryNodeInputImage' and getattr(nd,'image',None)):
            rep.append((owner, getattr(getattr(nd,'image',None),'name',None),'GN'))
for m in bpy.data.materials:
    if m.node_tree: fix_tree(m.node_tree,'mat:'+m.name)
for g in bpy.data.node_groups: fix_tree(g,'ng:'+g.name)
for w in bpy.data.worlds:
    if w.node_tree: fix_tree(w.node_tree,'world:'+w.name)
# GN modifier image inputs
for o in bpy.data.objects:
    for md in o.modifiers:
        if md.type=='NODES':
            for k in md.keys():
                v=md[k]
                if isinstance(v,bpy.types.Image) and v.name in names: rep.append(('mod:'+o.name+'/'+md.name,v.name,'GNmod'))
print('REPLACED',json.dumps(rep)[:3000])
gn_used={r[1] for r in rep if r[2]!='shader'}
removed=[]
for im in strip:
    if im.name in gn_used: print('KEEP (GN use)',im.name); continue
    removed.append(im.name); bpy.data.images.remove(im)
print('REMOVED',removed)
for _ in range(3): bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
try: bpy.ops.file.pack_all()
except Exception as e: print('pack warn',e)
for l in list(bpy.data.libraries):
    if l.users==0: bpy.data.libraries.remove(l)
print('LIBS left',[l.filepath for l in bpy.data.libraries])
print('IMAGES',len(bpy.data.images),'unpacked',[i.name for i in bpy.data.images if not i.packed_file and i.source=='FILE'])
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True, copy=True)
print('SAVED',OUT)
