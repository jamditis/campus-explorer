# ws221: rename ws219 paint-mask tiles to the exporter's ws###x_mask_tile_N naming + 5-field tile lists (Codex PR #16 follow-up)
import json,shutil
D='/workspace/nj-scenes/montclair-state/data/'
M={'ws219a_mask_WS179_0.png':'ws219a_mask_tile_0.png','ws219a_mask_WS179_1.png':'ws219a_mask_tile_1.png',
   'ws219b_mask_WS130_2.png':'ws219b_mask_tile_2.png','ws219b_mask_WS135a_3.png':'ws219b_mask_tile_3.png',
   'ws219b_mask_WS138a_4.png':'ws219b_mask_tile_4.png','ws219z_mask_rhd_se_crosswalk.png':'ws219z_mask_tile_0.png'}
for a,b in M.items(): shutil.copyfile(D+a,D+b)
t8=json.load(open(D+'ws219b_mask_tiles.json'))
if len(t8[0])==8: json.dump(t8,open(D+'ws219ab_mask_tiles_8field.json','w'))  # original fix219b input, kept
else: t8=json.load(open(D+'ws219ab_mask_tiles_8field.json'))
for key in 'ab':
    json.dump([[M[t[1]],t[2],t[3],t[4],t[5]] for t in t8 if t[0]==key],open(D+'ws219%s_mask_tiles.json'%key,'w'))
z=json.load(open(D+'ws219z_mask_tiles.json'))
json.dump([[M.get(t[0],t[0])]+t[1:] for t in z],open(D+'ws219z_mask_tiles.json','w'))
for k in 'abz': print(k,json.load(open(D+'ws219%s_mask_tiles.json'%k)))
