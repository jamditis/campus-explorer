import bpy, os, random, math
A='/workspace/nj-scenes/assets/campus_assets.blend'
want=['Shrub_Boxwood','Shrub_Yew','Shrub_Azalea']
with bpy.data.libraries.load(A) as (s,d):
    have=[n for n in want if n in s.objects]; d.objects=have
print('SW99 have',have)
src=[o for o in d.objects if o]
old=[o for o in bpy.data.objects if o.name.startswith('WS99_bed_shrub_')]
coll=old[0].users_collection[0]
random.seed(199)
pick={0:'Shrub_Yew',1:'Shrub_Yew',2:'Shrub_Azalea',3:'Shrub_Boxwood',4:'Shrub_Yew',5:'Shrub_Azalea',6:'Shrub_Boxwood',7:'Shrub_Azalea',8:'Shrub_Boxwood'}
dims={}
for o in src:
    dims[o.name]=(o.dimensions.z/max(o.scale.z,1e-6), max(o.dimensions.x/max(o.scale.x,1e-6),o.dimensions.y/max(o.scale.y,1e-6)))
print('SW99 dims',dims)
for o in old:
    i=int(o.name.split('_')[3]); h=float(o.name.split('LiDARh')[1].split('_')[0])
    sn=pick.get(i,'Shrub_Boxwood'); sn=sn if sn in bpy.data.objects else src[0].name
    s=bpy.data.objects[sn]
    n=s.copy(); n.name='WS99_bed_shrub_%02d_%s_LiDARh%.1f_UNVERIFIED'%(i,sn.split('_')[1],h); coll.objects.link(n)
    hz,wd=dims[sn]; sz=min(h,1.6)/hz; sx=min(sz, 1.5/wd) if wd>0 else sz
    n.location=o.location; n.rotation_euler=(0,0,random.uniform(0,6.28)); n.scale=(sx*random.uniform(0.9,1.1),sx*random.uniform(0.9,1.1),sz)
    bpy.data.objects.remove(o)
for o in src:
    if o.name in bpy.data.objects and not o.users_collection: pass
print('SW99 swapped',len(old))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SW99 SAVED')
