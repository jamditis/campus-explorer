// fix-ups for materials the export categorised by name only
export function fixCat(name, cat) {
  // water of the scripted build (blender/scripted, kind "water"), whatever an older export filed it as
  if (/^SW_water_/.test(name)) return 'water';
  if (cat === 'glass' && /lawn|grass|turf/i.test(name)) return 'grass';
  // fence fabric and netting exported as glass (anything see-through was): they are metal you can see through
  if (cat === 'glass' && /chain.?link|netting|goal_net/i.test(name)) return 'metal';
  // white line paint filed as grass (Lot 9 stalls, Sprague field lines) was retinted lawn green: keep it paint
  if (cat === 'grass' && /paint|stripe|marking/i.test(name) && !/lawn|nostripe/i.test(name)) return '';
  // synthetic turf filed as lawn (Pittser Field's fs_turf): the exporter gives turf its own category only
  // for SW_ names. As lawn it took the lawn tone, the lawn texture and grass tufts.
  if (cat === 'grass' && /turf/i.test(name) && !/lawn|grass/i.test(name)) return 'turf';
  if (cat === 'asphalt' && /slot_/i.test(name)) return /brick/i.test(name) ? 'brick' : '';
  if (cat === 'asphalt' && /concrete/i.test(name)) return 'concrete'; // e.g. KX_drive_concrete
  if (cat === 'asphalt' && /atlas|_tv_|screen/i.test(name)) return ''; // signage textures filed as asphalt
  // "field" in fieldstone matched the exporter's grass regex; "bed_" on a concrete curb matched mulch
  if (cat === 'grass' && /stone|granite|marble|limestone/i.test(name) && !/lawn|grass|turf|skirt|terrain/i.test(name)) return 'stone';
  if (cat === 'mulch' && /concrete|curb|kerb/i.test(name) && !/mulch|chip|shredded|soil/i.test(name)) return 'concrete';
  // stainless/aluminium filed as concrete (name matched curb/stair/deck) lose their metalness
  if (/stainless|alumin/i.test(name) && cat !== 'glass') return 'metal';
  // a painted building plinth is not lawn; "cogen" plus grass was retinted green
  if (cat === 'grass' && /plinth/i.test(name) && !/lawn|grass|turf|skirt|terrain/i.test(name)) return 'concrete';
  if (cat) return cat;
  if (/amphi/i.test(name) && /stone|nosing|fieldstone/i.test(name)) return 'stone';
  if (/^Bark_/i.test(name)) return 'bark';
  if (/barrel_tile|tile_course|Eave_tile/i.test(name)) return 'rooftile';
  if (/soffit|fascia/i.test(name)) return 'plaster';
  if (/BD_osm_light|BD_fill_massing/i.test(name)) return 'concrete';
  return '';
}

/**
 * True for a see-through material that is not glazing: fence fabric, netting. It keeps its own category
 * and stays see-through; every other see-through material is treated as window or lamp glass.
 */
export function isSeeThroughSolid(name, cat) {
  const c = fixCat(name, cat);
  return c !== '' && c !== 'glass';
}

/**
 * True for clear glazing (windows, glass doors and partitions, a clear bottle). False for glass that
 * is not looked through: screens, lenses, frosted, dark or opal glass, fibreglass. Inside a building
 * with a real interior only clear glazing is drawn see-through (look.js).
 */
export function isClearGlass(name) {
  return !/screen|monitor|lens|frost|opal|dark|fibreglass|fiberglass|mirror|led\b|_tv_|tvm/i.test(name);
}
