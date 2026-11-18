import bpy, hashlib
h=hashlib.sha1()
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.type=='MESH' and ('Feliciano' in o.name):
        for v in o.data.vertices: h.update(('%.4f%.4f%.4f'%tuple(v.co)).encode())
        h.update(','.join(sorted(a.name for a in o.data.attributes)).encode())
print('COHASH',h.hexdigest()[:12])
