import bpy, os
# nx: nu render chain. Render-time only (not saved): for OBLIQUE aerials ('plan' not in the cam name) keep the CCOM tower
# shaft visible (ng's aerial hide list removes it, which left the tower's arch frames/trim floating as white hoops).
_c=os.environ['CAMS'].split(',')
_ren=[]
if os.environ.get('KEEPTOWER','1')=='1' and _c and all(('aerial' in c and 'plan' not in c) or 'aerial' not in c for c in _c):
    for o in bpy.data.objects:
        if o.name.startswith('CCOM tower 4a shaft'): _ren.append((o,o.name)); o.name='KEEP '+o.name
exec(open('scripts/nu/nu_render.py').read())
for o,n in _ren: o.name=n
