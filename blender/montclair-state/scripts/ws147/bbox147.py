import bpy, resource, json, sys
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=open('/workspace/nj-scenes/montclair-state/scripts/ws147/objnames.txt').read().split('\n')
out=open('/workspace/nj-scenes/montclair-state/scripts/ws147/bboxes.jsonl','w')
B=int(sys.argv[-1]) if sys.argv[-1].isdigit() else 400
for s in range(0,len(names),B):
    chunk=names[s:s+B]
    with bpy.data.libraries.load(P, link=False) as (src,dst):
        dst.objects=chunk
    for o in dst.objects:
        if o is None: continue
        try:
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]
            r=dict(n=o.name,t=o.type,bb=[round(min(c.x for c in bb),2),round(max(c.x for c in bb),2),round(min(c.y for c in bb),2),round(max(c.y for c in bb),2),round(min(c.z for c in bb),2),round(max(c.z for c in bb),2)],
                   mats=[sl.material.name for sl in o.material_slots if sl.material][:6],
                   mods=[(m.type,getattr(getattr(m,'node_group',None),'name',None)) for m in o.modifiers][:4],
                   hr=o.hide_render, par=o.parent.name if o.parent else None)
            out.write(json.dumps(r)+'\n')
        except Exception as e: out.write(json.dumps(dict(n=o.name,err=str(e)))+'\n')
    out.flush()
    for o in list(dst.objects):
        if o: bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    print("CHUNK",s,"RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, flush=True)
print("DONE")
