import bpy, os, bmesh, mathutils
# nt: nq render chain + for cutaway cams (render-time only, not saved): the 2F slab/soffit/ceilings and everything standing on the 2F
# over the 1F open floor (x -2.3..12.3, y 6.9..14.1; the 2F back hallway stays, there is no 1F floor under it) hidden, and the inward room-shell boxes lose their lid faces so the aerial looks into the rooms.
cams=os.environ['CAMS'].split(','); _nt=[]; _sw=[]
def _bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
if any('cutaway' in c for c in cams):
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render: continue
        lo,hi=_bb(o)
        if lo[0]>-2.3 and hi[0]<12.3 and lo[1]>6.9 and hi[1]<14.1 and lo[2]>141.3: _nt.append(o)
        elif o.name.startswith(('NG 2F hallway slab','NG 2F hallway ceiling','NG double-height ceiling','CCOM back rooms lay-in ceilings','CCOM back rooms 2x2 troffers','CCM office lay-in ceiling','CCM office 2x2 troffers','CCOM_east_roof_plate_z2','CCOM_east_flat_roof_clean','CCOM_Win_Wing_A_ceil')): _nt.append(o)
        elif lo[0]>-0.8 and hi[0]<7.8 and lo[1]>3.2 and hi[1]<18.1 and lo[2]>140.5 and o.name.startswith(('NO ','NQ ','NP ','NK ')): _nt.append(o)   # room ceiling grids/devices over the lidless room shells
    for o in bpy.data.objects:
        if o.type=='MESH' and not o.hide_render and 'room shell' in o.name and len(o.data.vertices)==8:
            me=o.data.copy(); bm=bmesh.new(); bm.from_mesh(me); zt=max(v.co.z for v in bm.verts)
            kill=[f for f in bm.faces if all(abs(v.co.z-zt)<1e-4 for v in f.verts)]
            bmesh.ops.delete(bm,geom=kill,context='FACES_ONLY'); bm.to_mesh(me); bm.free(); _sw.append((o,o.data)); o.data=me
    for o in _nt: o.hide_render=True
    print('NT cutaway hides',len(_nt),'shell lids',len(_sw)); [print('NT hide|',o.name) for o in _nt]
exec(open('scripts/nq/nq_render.py').read())
for o in _nt: o.hide_render=False
for o,d in _sw: o.data=d
