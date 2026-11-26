# ws250 pass 3 (CHAIN on ws250b): the subdivide selection only took faces CENTRED in the W63 box, so big fan faces centred east of
# x -142 (lawn N of Dickson, x -164..-144, y 182..202) or south of y 141 (Feliciano/Dickson passage x -184..-180) kept straight
# edges (still 0.3-1.3 m low). Selection box widened to x -196..-90, y 95..216 (subdividing outside the LiDAR target changes no
# heights: the re-snap weight is 0 where the target ray misses). University Hall (y >= 221) is not in main; nothing there.
import bpy
TAG='F250C'; ng=bpy.data.node_groups['WS250_W63_LiDAR_terrain_snap']; n=0
sd=ng.nodes['WS250_subdiv']; sg=sd.inputs['Mesh'].links[0].from_node
# walk the selection's compare nodes feeding the separate node
seen=set(); st=[sg.inputs['Selection'].links[0].from_node]
while st:
    x=st.pop()
    if x.name in seen: continue
    seen.add(x.name)
    if x.type=='COMPARE':
        v=round(x.inputs[1].default_value,1); m={-194.0:-196.0,-142.0:-90.0,141.0:95.0,213.0:216.0}
        if v in m: x.inputs[1].default_value=m[v]; n+=1
    for i in x.inputs:
        for l in i.links: st.append(l.from_node)
print(TAG,'thresholds changed',n,flush=True)
