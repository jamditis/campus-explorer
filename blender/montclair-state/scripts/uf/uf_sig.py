import bpy, hashlib, os
out = os.environ.get('OUT', '/workspace/nj-scenes/montclair-state/data/uf/sig.txt')
objs = sorted(o.name for o in bpy.data.objects)
mats = sorted(m.name for m in bpy.data.materials)
meshes = sorted(m.name for m in bpy.data.meshes)
cams = sorted(c.name for c in bpy.data.cameras)
# include soft-end attr presence + UE hide state for exactness
extra = []
for name in (
    'UA_NormalAve_CR618_583841725_727_729_UNVERIFIED',
    'UA_CollegeAve_spur_1557427669_UNVERIFIED',
    'UA_SkylineWay_south_232846698_UNVERIFIED',
):
    o = bpy.data.objects.get(name)
    if not o:
        extra.append(f'{name}:MISS')
        continue
    has = 'uf_end_fade' in o.data.attributes
    mats_o = ','.join(s.material.name if s.material else '-' for s in o.material_slots)
    extra.append(f'{name}:fade={int(has)}:mats={mats_o}')
ue = bpy.data.objects.get('UE_Cole_east_arched_GF_UNVERIFIED')
if ue:
    extra.append(f'UE_arch:hv={int(ue.hide_viewport)}:hr={int(ue.hide_render)}')
blob = '|'.join([
    f'O{len(objs)}', f'M{len(mats)}', f'E{len(meshes)}', f'C{len(cams)}',
    hashlib.sha1('\n'.join(objs).encode()).hexdigest()[:12],
    hashlib.sha1('\n'.join(mats).encode()).hexdigest()[:12],
    hashlib.sha1('\n'.join(meshes).encode()).hexdigest()[:12],
    hashlib.sha1('\n'.join(extra).encode()).hexdigest()[:12],
])
open(out, 'w').write(f'UFSIG {len(objs)} {len(mats)} {len(meshes)} {len(cams)} {blob}\n' + '\n'.join(extra) + '\n')
print(open(out).read().strip())
