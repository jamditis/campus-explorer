import bpy
def hit(o,b):
    mw=o.matrix_world
    xs=[(mw@__import__('mathutils').Vector(c)) for c in o.bound_box]
    return not(max(v.x for v in xs)<b[0] or min(v.x for v in xs)>b[1] or max(v.y for v in xs)<b[2] or min(v.y for v in xs)>b[3])
for b in [(-75,-55,-300,-190),(-125,-90,-295,-262)]:
    print('BOX',b)
    for o in bpy.data.objects:
        if o.type=='MESH' and hit(o,b): print(' ',o.name,len(o.data.polygons),[m.name for m in o.data.materials][:2],o.hide_render)
