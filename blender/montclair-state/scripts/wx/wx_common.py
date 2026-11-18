G=['WV_stone_west_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED']
S=['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED','QS_service_546643370_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED','QW_soil_edge_546643369_ext_UNVERIFIED','QW_service_546643370_ext_UNVERIFIED','SG_QuadRoad_full_313028548_549_UNVERIFIED','TR_footway_546643369_S_gap_UNVERIFIED']
H=['TI_Stone_Hall_313028565_lower_UNVERIFIED','TQ_Stone_fascia_lower_UNVERIFIED']
def bv(n):
    o=O[n]; m=o.data; return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons])
SB={n:bv(n) for n in S}; HB={n:bv(n) for n in H}
def top(B,x,y):
    z=None
    for b in B.values():
        r=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if r[0] is not None and (z is None or r[0].z>z): z=r[0].z
    return z
def inside(x,y): return top(HB,x,y) is not None
