import bpy, os, bmesh, mathutils
# nq: np render chain; for cutaway cams also strip rooftop hood/vent islands over the CCOM cut region (render-time only, not saved)
cams=os.environ['CAMS'].split(',')
_swap=[]
if any('cutaway' in c for c in cams):
    for n in ('el roof exhaust fan hoods (generic, UNVERIFIED type)','Roof_vent'):
        o=bpy.data.objects.get(n)
        if not o or o.type!='MESH': continue
        me=o.data.copy(); bm=bmesh.new(); bm.from_mesh(me); M=o.matrix_world
        bm.verts.ensure_lookup_table(); kill=set(); seen=set()
        for v in bm.verts:
            if v.index in seen: continue
            st=[v]; comp=[]; seen.add(v.index)
            while st:
                x=st.pop(); comp.append(x)
                for e in x.link_edges:
                    w=e.other_vert(x)
                    if w.index not in seen: seen.add(w.index); st.append(w)
            c=sum((M@q.co for q in comp),mathutils.Vector())/len(comp)
            if -23<c.x<16 and -16<c.y<28: kill.update(comp)
        bmesh.ops.delete(bm,geom=list(kill),context='VERTS'); bm.to_mesh(me); bm.free()
        print('NQ cut islands from',n,len(kill),'verts'); _swap.append((o,o.data)); o.data=me
exec(open('scripts/np/np_render.py').read())
for o,d in _swap: o.data=d
