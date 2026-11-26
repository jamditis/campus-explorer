# ws246 W62d: pale seam where the east stand's S end meets the ground = the skirt / Feliciano SW edge-feather faces just
# past the stand end tinted by ortho texels of the stand seats/pad/deck (pale grey). Same lawn-texel UV remap as f246a,
# on those two objects, S-end box only, vertices within 6 m of the stands/pitch targets.
import os
for ob,tag in (('PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','F246B'),('Context_skirt_3DEP_ortho_4km','F246B2')):
    if ob not in bpy.data.objects: print(tag,'missing',ob,flush=True); continue
    os.environ.update(F246BOX='-258,-212,28,72',F246TAG=tag,F246OBJ=ob,F246MG='6')
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws246/f246a.py').read())
for k in ('F246BOX','F246TAG','F246OBJ','F246MG'): os.environ.pop(k,None)
