import bpy
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']
s=[len(bpy.data.objects),len(bpy.data.images),len(m.node_tree.nodes),len(m.node_tree.links)]
for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
    for i in n.inputs:
        if hasattr(i,'default_value') and not i.is_linked:
            try: s.append((n.name,i.name,round(float(i.default_value),4)))
            except: pass
    if hasattr(n,'image') and n.image: s.append(n.image.name)
f=bpy.data.materials['BD_farfield_ortho_haze_bm']
s+=[n.image.name for n in f.node_tree.nodes if getattr(n,'image',None)]
s+=[(o.data.name,len(o.data.polygons)) for o in bpy.data.objects if o.name=='BD_farfield_3DEP_ortho' and o.library is None]
import hashlib; print('SIG',hashlib.md5(repr(s).encode()).hexdigest(),s[:4],s[-2:])
