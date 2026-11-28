# ws269: filter paint269.json strokes (drop car glare, tree, turn-arrow and car-side boxes, ortho pixel boxes) and add the island axis
import json,numpy as np
D=json.load(open('paint269.json')); X0=-398;Y1=-12;S=0.1
wb=lambda c0,r0,c1,r1:(X0+c0*S,Y1-r1*S,X0+c1*S,Y1-r0*S)
DROP=[wb(440,195,560,235),wb(378,238,402,282),wb(572,232,608,258),wb(692,260,728,288),wb(160,203,225,248)]
keep=[s for s in D['segs'] if not any(a<=(s[0]+s[2])/2<=c and b<=(s[1]+s[3])/2<=d for a,b,c,d in DROP)]
json.dump(dict(segs=keep,island=dict(a=[-357.5,-36.6],b=[-334.5,-40.9],w=2.6)),open('paint269k.json','w')); print(len(D['segs']),'->',len(keep))
