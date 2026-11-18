import bpy, hashlib, os
out = os.environ.get('OUT', '/workspace/nj-scenes/montclair-state/data/ud/sig.txt')
objs = sorted(o.name for o in bpy.data.objects)
mats = sorted(m.name for m in bpy.data.materials)
meshes = sorted(m.name for m in bpy.data.meshes)
cams = sorted(c.name for c in bpy.data.cameras)
blob = '|'.join([
    f'O{len(objs)}', f'M{len(mats)}', f'E{len(meshes)}', f'C{len(cams)}',
    hashlib.sha1('\n'.join(objs).encode()).hexdigest()[:12],
    hashlib.sha1('\n'.join(mats).encode()).hexdigest()[:12],
    hashlib.sha1('\n'.join(meshes).encode()).hexdigest()[:12],
])
open(out, 'w').write(
    f'UDSIG {len(objs)} {len(mats)} {len(meshes)} {len(cams)} {blob}\n')
print(open(out).read().strip())
