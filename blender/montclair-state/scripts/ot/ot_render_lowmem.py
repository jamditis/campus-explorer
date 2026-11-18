# ot: low-memory wrapper around the established od/oc render chain (box has ~2.5 GB available): texture limit + small tiles.
import bpy, os
s=bpy.context.scene; s.render.use_simplify=True
s.cycles.texture_limit_render=os.environ.get('TEXLIM','1024'); s.cycles.use_auto_tile=True; s.cycles.tile_size=int(os.environ.get('TILE','256'))
s.render.use_persistent_data=False
s.cycles.use_camera_cull=True; s.cycles.camera_cull_margin=float(os.environ.get('CULLM','0.15'))
nc=0
for o in s.objects:
    n=o.name.lower()
    if any(k in n for k in ('grass','leaves','lawn','clover','weed')) and o.type in ('MESH','POINTCLOUD','CURVES'):
        o.cycles.use_camera_cull=True; nc+=1
print('CULL',nc)
print('LOWMEM',s.cycles.texture_limit_render,s.cycles.tile_size)
exec(open('scripts/od/od_render.py').read())
