
## 2026-10-14: Montclair Heights station added (Joe asked on Oct 14, 9:07 AM ET)
- NJ Transit Montclair Heights (OSM node 7009814496, 40.8576232, -74.2025840; local -454.1, -266.1). Checked against the NJ 2020 ortho: two tracks, two low side platforms, a brick shelter on the west side, parking to the east, and the Normal Ave grade crossing just north.
- 303 m at grid bearing 214° from the Red Hawk Deck centroid. 1,432 m at 197° from the MSU station. It was OUTSIDE the old polygon (south edge about y -110).
- Polygon extended: base ∪ box(-485,-372,-400,-95) (station, platforms, shelters, crossing, immediate parking) ∪ box(-420,-240,-382,-15) (walk up Carlisle Rd toward the Red Hawk Deck). Area went from 268,360 to 295,767 m². Previous version: data/boundary_20261014a_pre_mh.json. Script: north/scripts/mh_station_20261014.py.
- 2026-10-14 9:31 AM ET: Joe asked for Sprague Field (OSM 232846653, centroid -336, -157, between the station and the Red Hawk Deck). It was outside, so the polygon was extended by the pitch's rotated rectangle + 26 m (stands, press box, lights, fence). Area is now 313,426 m² (106 pts), applied by mh_station_20261014.py.


## Joe clarification — Nov 6, 2026, 6:26 PM ET
Building glass should be a little more reflective wherever an accurate interior has not been modeled. Prefer modest sky/environment reflection over exposing empty shells. This applies across the NJ scenes, not just Freeman. Retain see-through glass where an accurate interior exists. Apply in the next material pass; do not ask Joe again about mirror versus see-through preference.


## Joe clarification — Nov 6, 2026, 6:27 PM ET
After three consecutive progress updates without a reply from Joe, resolve outstanding modeling questions with best judgment rather than waiting. Record each decision, its rationale, and what remains UNVERIFIED so Joe can get a concise catch-up when he returns. Track unanswered consecutive updates; a reply resets the count. This is modeling discretion, not permission to send external messages, purchase, delete, or take other consequential actions.

- 2026-11-08 Joe: the arches on the RED HAWK COUNTRY wall are PAINTED ON (flat wall, arches + letters are a painted texture/decal) - do not model them as recessed/3D arches.

## Decision — Nov 9, 2026, ~6:45 AM ET (session wn, under Joe's Nov 6 three-unanswered-updates rule)
PLAN row 12 (Student Recreation Center, Dinallo Heights, Machuga Heights) is treated as OUTSIDE the current boundary: none of the three is named here or in north/data/boundary.json, and Joe has not answered the boundary question (asked 9:45 PM Nov 7, repeated in seven Nov 8 updates). They are NOT modeled and the polygon is NOT extended. UNVERIFIED decision; if Joe says they belong in, extend the polygon and give them a building day.

## Joe decision — Nov 9, 2026, 8:45 AM ET
Include Normal Ave, Clove Road and Valley Road as in-scope edge streets for day-13 streetscape work (together with Carlisle Road and Webster Road). Earlier survey note that those three lie outside the polygon is overridden for modelling scope: hourly :17 sessions will build the edge streetscapes (draped asphalt / curbs only where the 2020 ortho shows them). Polygon extension may follow if a stretch needs ground beyond the current boundary; do not invent buildings beyond the edge. Recorded as Joe's explicit ask ("let's include those roads").

## Joe clarification — Nov 9, 2026, 8:46 AM ET
Priority modelling/render corridor is **Red Hawk → Cole Hall → CCOM**. "Red Hawk" here means the Red Hawk Deck / College Avenue / Red Hawk Country wall approach on the west side of campus (Red Hawk Diner / Red Hawk Central / Red Hawk Deck cluster; the painted RED HAWK COUNTRY arcade wall location is still UNVERIFIED — check before modelling). Edge-street work (Normal Ave, Clove Rd, Valley Rd, Carlisle Rd, Webster Rd) should prioritise stretches that serve this corridor (especially Normal Ave / College Ave near CCOM–Cole–Red Hawk Deck). Student Rec / Dinallo / Machuga remain outside unless Joe revisits that.
