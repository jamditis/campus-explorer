# Rule 16 scan of published tiles: node/mesh/material names that suggest interiors, with node world-ish translation.
import json, struct, sys, re, glob
K = re.compile(r'room|interior|floor_?plan|corridor|hallway|partition|bedroom|suite|lounge|furn|desk|bed\b|ceiling|label|lobby|stair', re.I)
for f in sorted(glob.glob(sys.argv[1])):
    b = open(f, 'rb').read()
    n = struct.unpack_from('<I', b, 12)[0]
    j = json.loads(b[20:20 + n])
    names = [('node', x.get('name', ''), x.get('translation')) for x in j.get('nodes', [])]
    names += [('mesh', x.get('name', ''), None) for x in j.get('meshes', [])]
    names += [('mat', x.get('name', ''), None) for x in j.get('materials', [])]
    hits = [h for h in names if K.search(h[1])]
    print(f.split('/')[-1], len(j.get('nodes', [])), 'hits', len(hits))
    for h in hits[:15]: print('   ', h[0], h[1][:80], [round(v) for v in h[2]] if h[2] else '')
