# ws262 M4b verify 2 (NO SAVE): ortho2020_north.jpg path after localising; material name variants (.001) that share a base name
import bpy, os, collections
TAG='C262F'
for i in bpy.data.images:
    if 'north' in i.name.lower() or 'north' in i.filepath: print(TAG,'IMG',i.name,i.filepath,i.library,os.path.exists(bpy.path.abspath(i.filepath)),i.users,flush=True)
b=collections.defaultdict(list)
for m in bpy.data.materials: b[m.name.split('.')[0]].append((m.name,m.users,m.library.name if m.library else None))
print(TAG,'dups',[v for k,v in b.items() if len(v)>1 and any(x[0].startswith(('bv_','dN2','dJ','North','cv_','cw_','bt_','bw_','bx_')) for x in v)][:10],flush=True)
os._exit(0)
