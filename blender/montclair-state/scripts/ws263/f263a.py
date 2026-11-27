# ws263 M5 (merge208 CHAIN): main must not read anything under north/ (one-file merge; north/ is to be retired later, NOT deleted
# here). census263a: 28 image datablocks -> 9 files under north/data/ (ortho2020_north.jpg, paving_mask.png, ground-class /
# tone / mask PNGs, cogen_ground_he.exr; 4.5 MB). The files were copied byte-identical (sha256 north_carry263.sha256) to
# //data/north_carry/<same sub-path>; this repoints each datablock there (relative path), reloads nothing else.
import bpy, os
TAG='F263A'
root=os.path.dirname(bpy.data.filepath) if bpy.data.filepath else '/workspace/nj-scenes/montclair-state'
ND=os.path.join(root,'north','data')+'/'
n=0; miss=[]
for i in bpy.data.images:
    if not i.filepath or i.library: continue
    ab=os.path.normpath(bpy.path.abspath(i.filepath))
    if not ab.startswith(ND): continue
    rel=ab[len(ND):]
    new=os.path.join(root,'data','north_carry',rel)
    if not os.path.exists(new): miss.append(new); continue
    old=i.filepath
    i.filepath='//data/north_carry/'+rel
    n+=1; print(TAG,'repath',repr(i.name),old,'->',i.filepath,flush=True)
left=[i.name for i in bpy.data.images if i.filepath and '/north/' in os.path.normpath(bpy.path.abspath(i.filepath))]
print(TAG,'repathed',n,'missing',miss,'left under north/',left,flush=True)
if miss or left: raise SystemExit('F263A incomplete')
