import bpy, os
# nk: nj cutaway list + the entrance gable / eave returns / entrance soffit / tower hip roof over the atrium for cutaway cams only (render-only, restored after each camera)
src=open('scripts/nj/nj_render.py').read()
extra='''
for o in bpy.data.objects:
    cn=o.users_collection[0].name if o.users_collection else ''
    if cn in ('MS_CCOM_entrance_gable_20261029mt','MS_CCOM_gable_eave_returns_20261029mu') or o.name.startswith(('NH entrance soffit','CCOM tower 4a hip')):
        cut.append(o)
'''
src=src.replace("src=src.replace(\"for c in cams:\",extra+","src=src.replace(\"for c in cams:\",extra+EXTRA2+",1)
exec(src,{'EXTRA2':extra,'__name__':'nkr'})
