// fix-ups for materials the export categorised by name only
export function fixCat(name, cat) {
  if (cat === 'glass' && /lawn|grass|turf/i.test(name)) return 'grass';
  // white line paint filed as grass (Lot 9 stalls, Sprague field lines) was retinted lawn green: keep it paint
  if (cat === 'grass' && /paint|stripe|marking/i.test(name) && !/lawn|nostripe/i.test(name)) return '';
  if (cat === 'asphalt' && /slot_/i.test(name)) return /brick/i.test(name) ? 'brick' : '';
  if (cat === 'asphalt' && /concrete/i.test(name)) return 'concrete'; // e.g. KX_drive_concrete
  if (cat === 'asphalt' && /atlas|_tv_|screen/i.test(name)) return ''; // signage textures filed as asphalt
  // "field" in fieldstone matched the exporter's grass regex; "bed_" on a concrete curb matched mulch
  if (cat === 'grass' && /stone|granite|marble|limestone/i.test(name) && !/lawn|grass|turf|skirt|terrain/i.test(name)) return 'stone';
  if (cat === 'mulch' && /concrete|curb|kerb/i.test(name) && !/mulch|chip|shredded|soil/i.test(name)) return 'concrete';
  if (cat) return cat;
  if (/amphi/i.test(name) && /stone|nosing|fieldstone/i.test(name)) return 'stone';
  if (/^Bark_/i.test(name)) return 'bark';
  if (/barrel_tile|tile_course|Eave_tile/i.test(name)) return 'rooftile';
  if (/soffit|fascia/i.test(name)) return 'plaster';
  if (/BD_osm_light|BD_fill_massing/i.test(name)) return 'concrete';
  return '';
}
