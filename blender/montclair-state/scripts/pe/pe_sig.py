import bpy,hashlib
names=sorted(o.name+'|'+(o.data.name if o.data else '')+'|'+','.join((s.link+':'+(s.material.name if s.material else '')) for s in o.material_slots) for o in bpy.data.objects)
print('SIG',len(names),len(bpy.context.scene.objects),hashlib.sha1('\n'.join(names).encode()).hexdigest()[:12])
