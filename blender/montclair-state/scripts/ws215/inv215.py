import bpy, json
out=[]
for im in bpy.data.images:
    users=[]
    out.append(dict(n=im.name, fp=im.filepath, packed=bool(im.packed_file), size=list(im.size) if im.has_data else None, users=im.users, lib=bool(im.library)))
print("LIBS", [l.filepath for l in bpy.data.libraries])
json.dump(out, open('/workspace/nj-scenes/montclair-state/scripts/ws215/images.json','w'), indent=0)
print("N", len(out))
