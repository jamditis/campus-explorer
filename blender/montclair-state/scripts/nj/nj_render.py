import bpy, os, mathutils
# nj cutaway: nh_render list + everything above z 145.99 over the CCOM atrium/hall block (render-only, restored after each camera)
src=open('scripts/nh/nh_render.py').read()
extra='''
def _bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
for o in bpy.data.objects:
    if o.type=='MESH' and not o.hide_render:
        lo,hi=_bb(o)
        if lo[0]>-21.2 and hi[0]<14 and lo[1]>-14 and hi[1]<26 and lo[2]>145.99: cut.append(o)
        elif ('ceil' in o.name.lower() or 'roof' in o.name.lower()) and lo[0]>-21.2 and hi[0]<14 and lo[1]>-14 and hi[1]<26 and lo[2]>141: cut.append(o)
'''
src=src.replace("for c in cams:",extra+"\nfor c in cams:",1)
exec(src)
