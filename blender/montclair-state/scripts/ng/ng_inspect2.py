import bpy, mathutils
def bb(o):
    m=o.matrix_world; cs=[m@mathutils.Vector(c) for c in o.bound_box]
    return [round(min(c[i] for c in cs),2) for i in range(3)]+[round(max(c[i] for c in cs),2) for i in range(3)]
for c in bpy.data.collections:
    if not ('CCOM' in c.name or 'ccom' in c.name): continue
    obs=[o for o in c.objects if o.type=='MESH']
    if not obs: continue
    B=[bb(o) for o in obs]
    U=[min(b[i] for b in B) for i in range(3)]+[max(b[i] for b in B) for i in range(3)]
    print("COL",c.name,len(obs),"hr",c.hide_render,[round(u,1) for u in U])
    for o,b in zip(obs,B):
        d=max(b[3]-b[0],b[4]-b[1],b[5]-b[2])
        if d>3.5 and c.name in ('CCOM_1f_interior_full_dd','CCOM_east_interior_joe_20261020dc','CCOM_interior_20261014v','CCOM_lounge_photo_20261015al','CCOM_lounge_east_20261014jf','CCOM_east_massing_20261014y','CCOM_corridor_skirt_dV','CCOM_computer_lab_20261014y','CCOM_east_raised_box_20261014jf2','CCOM_east_glazing_20261014jf'):
            print("  BIG",o.name,b,"hr",o.hide_render)
# CCOM building shell objects
for o in bpy.data.objects:
    if o.type=='MESH' and ('School of Communication' in o.name or 'CCOM' == o.name[:4] and 'bldg' in o.name.lower() or 'osm' in o.name.lower() and 'ccom' in o.name.lower()):
        print("SHELL",o.name,bb(o))
