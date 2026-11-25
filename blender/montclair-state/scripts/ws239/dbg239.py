import bpy, json
def _pre(scene,*a):
    for n in json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws239/m2c_new239.json'))[:21]:
        o=bpy.data.objects.get(n)
        print('DBG239',n[:30],o and o.hide_render, o and o.visible_get(), o and [c.name for c in o.users_collection], o and o.name in scene.objects, flush=True)
bpy.app.handlers.render_pre.append(_pre)
