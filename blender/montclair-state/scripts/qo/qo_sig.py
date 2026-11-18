# qo SIG: objects / materials / meshes + sha of (object names+modifier names+mesh vert/face counts, image paths, Ground_ortho_grass node names/links, node group names)
import bpy, hashlib
h=hashlib.sha256()
for o in sorted(bpy.data.objects,key=lambda o:o.name):
  h.update(o.name.encode()); h.update(','.join(m.name for m in o.modifiers).encode())
  if o.type=='MESH': h.update(('%d/%d'%(len(o.data.vertices),len(o.data.polygons))).encode())
for i in sorted(bpy.data.images,key=lambda i:i.name): h.update((i.name+i.filepath).encode())
nt=bpy.data.materials['Ground_ortho_grass'].node_tree
for n in sorted(x.name for x in nt.nodes): h.update(n.encode())
for l in sorted('%s>%s.%s'%(l.from_node.name,l.to_node.name,l.to_socket.identifier) for l in nt.links): h.update(l.encode())
for g in sorted(x.name for x in bpy.data.node_groups): h.update(g.encode())
for c in sorted(x.name for x in bpy.data.collections): h.update(c.encode())
print('QO_SIG %d %d %d %s'%(len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),h.hexdigest()[:12]))
