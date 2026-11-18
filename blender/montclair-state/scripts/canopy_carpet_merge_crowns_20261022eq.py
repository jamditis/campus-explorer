"""tag 20261022eq (RERUNNABLE; SAVE=1 or --save; REVERT=1 removes). Far canopy carpet (ai/bl, 450 m-8 km) still read as
separate green balls through CCOM's east lounge window (eo/ep flag). Geometry-nodes only: after Instance on Points in every
MID_canopy_carpet_*_GN group, an EQ_scale Scale Instances node widens each crown in x/y (x1.40, height kept; a first try with z x0.80 read as flat pebbles) - trunk groups untouched,
so neighbouring crowns overlap into a continuous woodland canopy at eye level. Positions/counts unchanged
(NLCD canopy fraction still MEASURED per 30 m cell; crown size UNVERIFIED artistic)."""
import bpy, os, sys
SAVE=("--save" in sys.argv) or os.environ.get("SAVE")=="1"; REVERT=os.environ.get("REVERT")=="1"
SXY=float(os.environ.get("SXY","1.40")); SZ=float(os.environ.get("SZ","1.0"))
n_done=0
for ng in [g for g in bpy.data.node_groups if g.name.startswith("MID_canopy_carpet_") and "_GN" in g.name and "_trunks_" not in g.name]:
    N=ng.nodes; L=ng.links
    iops=[n for n in N if n.bl_idname=='GeometryNodeInstanceOnPoints']
    for n in [n for n in N if n.name.startswith("EQ_")]:
        # relink around it
        ins=n.inputs['Instances'].links; outs=list(n.outputs['Instances'].links)
        src=ins[0].from_socket if ins else None
        for l in outs:
            to=l.to_socket; L.remove(l)
            if src: L.new(src,to)
        N.remove(n)
    if REVERT: n_done+=1; continue
    for iop in iops:
        outs=list(iop.outputs['Instances'].links)
        si=N.new('GeometryNodeScaleInstances'); si.name=f"EQ_scale_{iop.name}"
        si.inputs['Scale'].default_value=(SXY,SXY,SZ)
        si.inputs['Local Space'].default_value=True
        L.new(iop.outputs['Instances'],si.inputs['Instances'])
        for l in outs:
            to=l.to_socket; L.remove(l); L.new(si.outputs['Instances'],to)
    ng["eq_merge_crowns"]=f"crowns x{SXY} xy, x{SZ} z, 20261022eq (UNVERIFIED artistic)"
    n_done+=1
    print("EQ_GROUP", ng.name, "iops", len(iops), "users", ng.users)
print("EQ_DONE", n_done, "reverted" if REVERT else "ok")
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")
