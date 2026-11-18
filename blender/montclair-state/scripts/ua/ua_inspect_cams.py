import bpy
from mathutils import Vector

def dims(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    lo=Vector((min(v.x for v in bb),min(v.y for v in bb),min(v.z for v in bb)))
    hi=Vector((max(v.x for v in bb),max(v.y for v in bb),max(v.z for v in bb)))
    return lo,hi

for name in ["UA_NormalAve_CR618_583841725_727_729_UNVERIFIED","UA_NormalAve_N_sidewalk_583841727_UNVERIFIED","UA_CollegeAve_spur_1557427669_UNVERIFIED","Context_skirt","Terrain"]:
    o=bpy.data.objects.get(name)
    if not o:
        print("MISS", name); continue
    lo,hi=dims(o)
    nvert=len(o.data.vertices) if o.type=="MESH" else -1
    print(name, "dx=%.1f dy=%.1f dz=%.2f" % ((hi-lo).x,(hi-lo).y,(hi-lo).z), "z=[%.1f,%.1f]" % (lo.z,hi.z), "verts", nvert)

cam_loc=Vector((-177.6,-282.6,120.3))
print("CAM_LOC", tuple(cam_loc))
hits=[]
for o in bpy.data.objects:
    if o.type!="MESH": continue
    lo,hi=dims(o)
    if lo.x-3<=cam_loc.x<=hi.x+3 and lo.y-3<=cam_loc.y<=hi.y+3 and lo.z-1<=cam_loc.z<=hi.z+3:
        hits.append((o.name, round(lo.z,1), round(hi.z,1), len(o.data.vertices)))
print("NEAR", sorted(hits, key=lambda t: -t[3])[:25])

# sample Context_skirt z near cam via BVH or nearest verts
sk=bpy.data.objects.get("Context_skirt")
if sk:
    # find verts near cam xy
    mw=sk.matrix_world
    near=[]
    for v in sk.data.vertices:
        w=mw@v.co
        if abs(w.x-cam_loc.x)<8 and abs(w.y-cam_loc.y)<8:
            near.append(w.z)
    if near:
        print("skirt_z_near_cam n=%d min=%.2f max=%.2f mean=%.2f" % (len(near), min(near), max(near), sum(near)/len(near)))
    else:
        print("no skirt verts within 8m of cam xy")

road=bpy.data.objects.get("UA_NormalAve_CR618_583841725_727_729_UNVERIFIED")
if road:
    mw=road.matrix_world
    near=[]
    for v in road.data.vertices:
        w=mw@v.co
        if abs(w.x-cam_loc.x)<15 and abs(w.y-cam_loc.y)<15:
            near.append((w.x,w.y,w.z))
    if near:
        zs=[p[2] for p in near]
        print("road_z_near n=%d min=%.2f max=%.2f" % (len(near),min(zs),max(zs)))
        print("sample", near[:5])
