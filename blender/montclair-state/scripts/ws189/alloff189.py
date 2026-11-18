# ws189 probe-only: turn off viewport eval of EVERY modifier + particle display at load_post (never save this session)
import bpy, os, re
KO=os.environ.get('KEEPOFF','.')
from bpy.app.handlers import persistent
STATE={}
@persistent
def _off(*a):
    n=0
    for o in bpy.data.objects:
        for m in getattr(o,'modifiers',[]):
            STATE[(o.name,m.name)]=m.show_viewport
            if m.show_viewport and re.search(KO,o.name): m.show_viewport=False; n+=1
    print('ALLOFF189',n,flush=True)
bpy.app.handlers.load_post.append(_off)
