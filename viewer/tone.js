// Material albedo fixes that do not depend on three.js (unit-tested from node --test).
// The exporter keeps a Mix/Multiply colour factor and drops any image not fed straight
// into Base Color. `color` is a three.js Color (or a stand-in with r,g,b and multiplyScalar).

const lum = c => c.r * 0.2126 + c.g * 0.7152 + c.b * 0.0722;

// Authored Base Color from scripts/ip/ip_amphi_build.py (session ip, last explicit
// albedos before the iq variation/dirt patch). The export collapses those textured
// shaders to white or to a pale mix factor; restore the authored colour when the
// shipped value is clearly brighter and no base-color map is present.
const AUTHORED = {
  'hn_amphi_seat_stone_blocks': [0.215, 0.176, 0.141],
  'hn_amphi_riser_coursed_stone': [0.15, 0.1, 0.068],
  'hn_amphi_base_fieldstone': [0.22, 0.15, 0.1],
  'io_amphi_aisle_stone': [0.275, 0.228, 0.184],
  'ip_amphi_aisle_nosing_worn': [0.34, 0.295, 0.245],
  'io_amphi_stage_concrete': [0.25, 0.218, 0.178],
};

const TURF = [0.03, 0.12, 0.04]; // COLOUR["turf"] in blender/scripted/ground.py (UNVERIFIED tone)

function setColor(color, rgb) {
  if (typeof color.setRGB === 'function') color.setRGB(rgb[0], rgb[1], rgb[2]);
  else { color.r = rgb[0]; color.g = rgb[1]; color.b = rgb[2]; }
}

export function fixTone(name, color, hasMap) {
  if (hasMap || !color) return color;
  if (/granite/i.test(name) && /curb/i.test(name)) {
    const l = lum(color);
    if (l > 0.5) color.multiplyScalar(0.44); // Granite002A mean ~0.44 linear
    return color;
  }
  // synthetic turf whose shader the export collapsed to a neutral grey (fs_turf, Pittser Field): use the
  // scripted builds' turf tone (blender/scripted/ground.py), not a grey or a lawn green
  if (/turf/i.test(name) && !/lawn|grass|paint|line|stripe|marking/i.test(name)) {
    const hi = Math.max(color.r, color.g, color.b), lo = Math.min(color.r, color.g, color.b);
    if (hi - lo < 0.1 * hi) setColor(color, TURF);
    return color;
  }
  const authored = AUTHORED[name];
  if (authored) {
    const l = lum(color);
    const al = authored[0] * 0.2126 + authored[1] * 0.7152 + authored[2] * 0.0722;
    if (l > al * 1.6) setColor(color, authored);
  }
  return color;
}

// Stair stainless and aluminium nosings are exported with the right roughness
// (and often metalness), but look.js zeroes metalness and overwrites roughness
// once the category is not metal. Call after texturize so those values stick.
// Limit the restore to the stair parts that were mis-filed; other aluminium
// and stainless finishes keep their authored metalness. Authored: rail metal 1 /
// rough 0.22, nosing metal 0.8 / rough 0.38 (scripts/od/od_build.py).
export function finishMetal(name, mat) {
  if (!mat) return mat;
  if (/stair/i.test(name) && /stainless/i.test(name)) {
    mat.metalness = 1;
    if (mat.roughness > 0.22) mat.roughness = 0.22;
  } else if (/nosing/i.test(name) && /alumin/i.test(name)) {
    if (mat.metalness < 0.8) mat.metalness = 0.8;
    if (mat.roughness > 0.38) mat.roughness = 0.38;
  }
  return mat;
}
