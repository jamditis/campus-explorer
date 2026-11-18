import bpy, hashlib, os
out = os.environ.get('OUT', '/workspace/nj-scenes/montclair-state/data/up/sig.txt')
objs = sorted(o.name for o in bpy.data.objects); mats = sorted(m.name for m in bpy.data.materials)
meshes = sorted(m.name for m in bpy.data.meshes); cams = sorted(c.name for c in bpy.data.cameras)
extra = []
for n in ('SA_ground_lower_patch_UNVERIFIED','UG_Partridge_E_seam_fill_lawn_UNVERIFIED',
          'QXP_pedestrian_area_313024781_paving_UNVERIFIED','QY_plaza_rim_band_313024781_UNVERIFIED',
          'Footpaths_OSM','TY_footway_313026404_to_Partridge_UNVERIFIED',
          'TY_footway_313026399_to_Partridge_UNVERIFIED',
          'TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)',
          'UH_Partridge_E_seam_grass_points_UNVERIFIED',
          'UI_Partridge_E_strip_grass_points_UNVERIFIED',
          'UJ_Partridge_E_strip_grass_fill_UNVERIFIED',
          'UK_Partridge_E_strip_grass_fill_UNVERIFIED',
          'UL_Partridge_E_strip_grass_fill_UNVERIFIED',
          'UM_Partridge_E_strip_grass_fill_UNVERIFIED',
          'UN_Partridge_E_strip_grass_fill_UNVERIFIED',
          'UO_Partridge_E_strip_grass_fill_UNVERIFIED',
          'UP_Partridge_E_strip_grass_fill_UNVERIFIED'):
    o = bpy.data.objects.get(n)
    if not o: extra.append(n + ':MISS'); continue
    me = o.data
    h = hashlib.sha1(b''.join(('%.4f,%.4f,%.4f;' % tuple(v.co)).encode() for v in me.vertices)).hexdigest()[:12]
    extra.append(f'{n}:{me.name}:{len(me.vertices)}:{len(me.polygons)}:{h}')
blob = '|'.join([f'O{len(objs)}', f'M{len(mats)}', f'E{len(meshes)}', f'C{len(cams)}',
    hashlib.sha1('\n'.join(objs).encode()).hexdigest()[:12], hashlib.sha1('\n'.join(mats).encode()).hexdigest()[:12],
    hashlib.sha1('\n'.join(meshes).encode()).hexdigest()[:12], hashlib.sha1('\n'.join(extra).encode()).hexdigest()[:12]])
open(out, 'w').write(f'UPSIG {len(objs)} {len(mats)} {len(meshes)} {len(cams)} {blob}\n' + '\n'.join(extra) + '\n')
print(open(out).read().strip())
