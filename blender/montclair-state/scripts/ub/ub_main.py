"""Session ub (Nov 5 2026 ~12:15 PM ET, MAIN): Joe spotted a 'giant hole' in the white building right of the courtyard in the
UA SW oblique. It is Freeman Hall (context massing 'Freeman Hall walls'), NOT Partridge: the wall strip's top verts were
DSM-sampled (124.7..146.1 m, south end only ~140.8-142) while the flat LiDAR roof slab sits at 147.0, leaving an open band
up to ~6 m tall -> camera saw straight into the empty shell. Fix: lift every wall top vert (z>135) to 147.05 so walls meet the
roof. Roof height is LiDAR (MEASURED); wall-top = roof is an assumption (UNVERIFIED). Original z saved in data/ub/freeman_walls_orig.json.
REVERT=1 restores exact original coords."""
import bpy, os, json
REV=os.environ.get('REVERT')=='1'; SAVE=os.environ.get('SAVE')=='1'
J='/workspace/nj-scenes/montclair-state/data/ub/freeman_walls_orig.json'
o=bpy.data.objects['Freeman Hall walls']; me=o.data
if REV:
    d=json.load(open(J))
    for k,z in d.items(): me.vertices[int(k)].co.z=z
    o.pop('ub_fix',None); me.update(); print('UB REVERTED',len(d))
    for c in [c for c in list(bpy.data.objects) if c.get('ub_obj')]:
        cd=c.data; bpy.data.objects.remove(c,do_unlink=True); bpy.data.cameras.remove(cd)
    print('UB cams removed')
else:
    if o.get('ub_fix'): raise SystemExit('UB already applied')
    TOPZ=147.05
    d={str(v.index):v.co.z for v in me.vertices if v.co.z>135.0}
    if not os.path.exists(J): json.dump(d,open(J,'w'))
    for k in d: me.vertices[int(k)].co.z=TOPZ
    o['ub_fix']=1; me.update(); print('UB lifted',len(d),'top verts to',TOPZ,'min orig',min(d.values()),'max',max(d.values()))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
