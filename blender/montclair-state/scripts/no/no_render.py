import bpy, os
# no: nk cutaway list + floating ceiling items (atrium/2F LED strips, atrium ceiling cans + washers, 2F diffusers) for cutaway cams only
sc=bpy.context.scene
sc.render.use_simplify=True; sc.cycles.texture_limit_render='2048'
src=open('scripts/nj/nj_render.py').read()
extra='''
for o in bpy.data.objects:
    cn=o.users_collection[0].name if o.users_collection else ''
    if cn in ('MS_CCOM_entrance_gable_20261029mt','MS_CCOM_gable_eave_returns_20261029mu') or o.name.startswith(('NH entrance soffit','CCOM tower 4a hip')):
        cut.append(o)
    if o.name.startswith(('NG atrium LED','NG 2F hallway LED','NH 2F hallway ceiling diffuser','NK atrium downlight','NO atrium red-wall washer','NO atrium stair-side accent')) and o.type=='MESH':
        cut.append(o)
'''
src=src.replace("src=src.replace(\"for c in cams:\",extra+","src=src.replace(\"for c in cams:\",extra+EXTRA2+",1)
exec(src,{'EXTRA2':extra,'__name__':'nor'})
