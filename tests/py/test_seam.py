"""Two scripted areas side by side meet on the same vertices at the same heights.

Needs numpy (the test is skipped where it is missing).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

try:
    import geom
    import numpy as np
    import seam
except ImportError:  # no numpy on this machine
    np = None

# two areas that share the edge x = 100 from y 0 to 92.3; each is densified along its own
# outline, so their points on the shared edge do not coincide (92.3 / 47 against 279 / 140 m)
WEST = [(0, 0), (100, 0), (100, 92.3), (0, 92.3)]
EAST = [(100, 0), (300, 0), (300, 279), (100, 279)]


def dense(ring, step=2.0):
    return [(p[0], p[1]) for p in geom.resample(ring, step, True)]


def on_edge(ring):
    return sorted(round(p[1], 6) for p in ring if abs(p[0] - 100) < 1e-9 and p[1] <= 92.3 + 1e-9)


@unittest.skipIf(np is None, "numpy is not installed")
class SharedEdge(unittest.TestCase):
    def test_both_areas_get_the_same_vertices_on_the_shared_edge(self):
        west, east = dense(WEST), dense(EAST)
        self.assertNotEqual(on_edge(west), on_edge(east))
        west2 = geom.insert_on_ring(west, seam.points_on(WEST, [EAST]))
        east2 = geom.insert_on_ring(east, seam.points_on(EAST, [WEST]))
        a, b = on_edge(west2), on_edge(east2)
        # every vertex of one lies on a vertex of the other (within the insertion's 2 cm)
        for y in a:
            self.assertLess(min(abs(y - v) for v in b), 0.021)
        for y in b:
            self.assertLess(min(abs(y - v) for v in a), 0.021)

    def test_points_off_the_shared_edge_are_not_taken(self):
        pts = seam.points_on(WEST, [EAST])
        self.assertTrue(pts)
        for x, y in pts:
            self.assertAlmostEqual(x, 100.0)
            self.assertLessEqual(y, 92.3 + 1e-9)

    def test_a_later_area_takes_the_heights_the_first_one_gave_the_shared_vertices(self):
        s = seam.Seam()
        xy = np.array([[100.0, 10.0], [100.0, 12.0], [50.0, 0.0]])
        self.assertTrue(np.isnan(s.take(xy)).all())  # nothing recorded yet
        s.record(xy, np.array([5.0, 6.0, 7.0]))
        got = s.take(np.array([[100.0, 10.01], [100.0, 12.5], [100.0, 11.0]]))
        self.assertEqual(got[0], 5.0)  # within 2 cm: the recorded height
        self.assertTrue(np.isnan(got[1:]).all())  # anything further is the area's own

    def test_a_later_vertex_between_two_shared_ones_lies_on_the_first_areas_edge(self):
        # a vertex only the later area has on the shared edge (a corner of one of its surfaces,
        # an end point) kept its own height: a step to the first mesh's edge between its two
        # vertices (west and southwest at (-404.6, -57.5): 0.40 m in sw17)
        s = seam.Seam()
        xy = np.array([[100.0, 10.0], [100.0, 12.0], [100.0, 20.0]])
        s.record(xy, np.array([5.0, 6.0, 7.0]), edges=[(0, 1)])  # no edge from 12 to 20
        got = s.along(np.array([[100.0, 11.0], [100.01, 10.5], [100.0, 10.0], [100.5, 11.0],
                                [100.0, 16.0], [100.0, 9.0]]))  # fmt: skip
        self.assertAlmostEqual(got[0], 5.5)
        self.assertAlmostEqual(got[1], 5.25)  # within 2 cm of the edge
        self.assertAlmostEqual(got[2], 5.0)  # on its end
        self.assertTrue(np.isnan(got[3:]).all())  # off it, on no recorded edge, past its end

    def test_a_later_area_puts_the_first_areas_own_vertices_on_its_outline(self):
        # the first area's mesh had a vertex on the shared edge the later one lacked (a corner of
        # one of its surfaces): the later mesh's edge ran straight over it, a step (north-east and
        # stadium at (-66, 826): 0.28 m in sw17)
        s = seam.Seam()
        s.record(np.array([[100.0, 10.0], [100.0, 10.7], [100.0, 12.0], [50.0, 0.0]]),
                 np.array([5.0, 4.0, 6.0, 1.0]))  # fmt: skip
        got = sorted((round(x, 6), round(y, 6)) for x, y in s.on_ring(EAST))
        self.assertEqual(got, [(100.0, 10.0), (100.0, 10.7), (100.0, 12.0)])
        # less than 2 cm from a point the outline takes already: not again
        got = s.on_ring(EAST, skip=[(100.0, 10.71)])
        self.assertEqual(sorted(round(y, 6) for _x, y in got), [10.0, 12.0])

    def test_lot_paving_takes_a_shared_height_only_upward_where_sw17_had_no_shared_vertex(self):
        # a later area's lot met the first area's edge with a step of up to 7 cm where only one
        # mesh had a vertex: taking the first area's height there lowered the lot (AGENTS rule
        # 6). Other ground takes it either way, and so does a vertex both meshes had already
        own = np.array([10.0, 10.0, 10.0, 10.0, 10.0])
        known = np.array([9.9, 10.1, 9.9, 9.9, np.nan])
        lot = np.array([True, True, False, True, True])
        old = np.array([False, False, False, True, False])
        np.testing.assert_array_equal(seam.taken(known, own, lot, old),
                                      [False, True, True, True, False])  # fmt: skip

    def test_a_vertex_just_past_each_end_of_a_shared_edge_keeps_its_own_height(self):
        # WEST shares x 100 with EAST from y 0 to 92.3 and goes on from both ends as an edge with
        # no area beside it: a point 0.25 m along each of those edges from the corner, and none on
        # the shared edge (the vertices there take the first area's heights, sw16's flush seam)
        pts = seam.ends(WEST, [EAST])
        got = sorted((round(x, 6), round(y, 6)) for x, y in pts)
        self.assertEqual(got, [(99.75, 0.0), (99.75, 92.3)])
        # an edge shared all round a corner gives no point there
        inner = [(0, 0), (100, 0), (100, 92.3), (0, 92.3)]
        outer = [(-10, -10), (100, -10), (100, 0), (0, 0), (0, 92.3), (100, 92.3), (100, 200),
                 (-10, 200)]  # fmt: skip
        self.assertEqual(sorted((round(x, 6), round(y, 6)) for x, y in seam.ends(inner, [outer])),
                         [(100.0, 0.25), (100.0, 92.05)])  # fmt: skip


@unittest.skipIf(np is None, "numpy is not installed")
class EdgeSamples(unittest.TestCase):
    def test_samples_of_the_far_field_are_kept_up_to_the_end_of_a_shared_edge(self):
        # A shares x 10 with B from y 0 to 10; north and south of A past the corners lies far field.
        # Samples on the shared edge go (no other model to meet there). sw16 also dropped every
        # sample within 2 m of B: the first 2 m of A's far-field edges from each corner met no far
        # field (Lot 60 at its corner with the Village, (-212, 1281), stood 0.40 m over it)
        a = [(0, 0), (10, 0), (10, 10), (0, 10)]
        b = [(10, -5), (20, -5), (20, 30), (10, 30)]
        samples = [[p[0], p[1], 1.0] for p in geom.resample(a, 0.5, True)]

        def kept(others, near=None):
            got = seam.far_samples(samples, a, others, near)
            return {(round(s[0], 3), round(s[1], 3)) for s in got}

        k = kept([b])
        for p in ((10.0, 0.5), (10.0, 5.0), (10.0, 9.5), (10.0, 10.0), (10.0, 0.0)):
            self.assertNotIn(p, k)  # on the shared edge, its ends included
        for p in ((9.5, 10.0), (8.5, 10.0), (9.5, 0.0), (5.0, 10.0)):
            self.assertIn(p, k)  # the far-field edges up to the corners
        # edge heights made the first way keep sw16's rule
        k = kept([b], 2.0)
        self.assertNotIn((8.5, 10.0), k)
        self.assertIn((7.5, 10.0), k)
        # inside another area (areas that overlap a little) a sample goes too
        d = [(9, 3), (12, 3), (12, 6), (9, 6)]
        k = kept([d])
        self.assertNotIn((10.0, 4.5), k)
        self.assertIn((10.0, 8.0), k)


    def test_paving_keeps_the_samples_a_later_neighbour_took_away(self):
        # B arrived after A's paving was reviewed and asks that A's paving stay as it was: the
        # samples on the edge A now shares with B are held for A's paving; an older neighbour C's
        # edge keeps today's rule (its samples went long ago)
        a = [(0, 0), (10, 0), (10, 10), (0, 10)]
        b = [(10, -5), (20, -5), (20, 30), (10, 30)]
        c = [(-5, 10), (5, 10), (5, 20), (-5, 20)]
        samples = [[p[0], p[1], 1.0] for p in geom.resample(a, 0.5, True)]
        held = seam.held_samples(samples, a, [b, c], [b])
        got = {(round(s[0], 3), round(s[1], 3)) for s in held}
        self.assertIn((10.0, 5.0), got)  # on the edge shared with B: held for the paving
        self.assertNotIn((2.0, 10.0), got)  # on the edge shared with C: gone, as before
        self.assertEqual(seam.far_samples(samples, a, [c]), held)
        self.assertIsNone(seam.held_samples(samples, a, [b, c], []))  # no such neighbour

    def test_paving_keeps_the_samples_it_was_reviewed_with_when_the_edge_heights_change(self):
        # edge heights made again (sw18: read 5 cm outside instead of 0.3 m) would move paving
        # that is within 0.15 m of the far field; the file keeps the earlier samples under
        # "paving", and the paving is bent by those, filtered as the ground's are
        a = [(0, 0), (10, 0), (10, 10), (0, 10)]
        b = [(10, -5), (20, -5), (20, 30), (10, 30)]
        old = [[p[0], p[1], 1.0] for p in geom.resample(a, 0.5, True)]
        new = [[p[0], p[1], 2.0] for p in geom.resample(a, 0.5, True)]
        pave = {"samples": old, "source": "tiles, ground meshes 0.3 m outside"}
        got = seam.paving_samples(pave, new, a, [b], [])
        self.assertEqual({s[2] for s in got}, {1.0})
        self.assertFalse(any(s[0] == 10.0 and 0 < s[1] < 10 for s in got))  # shared: gone
        # held by a later neighbour: the shared edge's samples stay for the paving
        got = seam.paving_samples(pave, new, a, [b], [b])
        self.assertTrue(any(s[0] == 10.0 and 0 < s[1] < 10 for s in got))
        # nothing kept: paving follows the ground (None), unless a neighbour holds it
        self.assertIsNone(seam.paving_samples(None, new, a, [b], []))
        self.assertEqual({s[2] for s in seam.paving_samples(None, new, a, [b], [b])}, {2.0})
