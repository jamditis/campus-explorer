import test from 'node:test';
import assert from 'node:assert/strict';
import { fixCat, isSeeThroughSolid } from '../viewer/cat.js';

test('a category from the export is kept when nothing is known against it', () => {
  assert.equal(fixCat('WS27_curb_concrete_UNVERIFIED', 'concrete'), 'concrete');
  assert.equal(fixCat('SW_turf_painted_p013_0', 'turf'), 'turf');
  assert.equal(fixCat('SW_asphalt_painted_p009_1', 'asphalt'), 'asphalt');
});

test('known misfilings are corrected', () => {
  assert.equal(fixCat('WS172_lawn_fade_nostripe_WS175', 'glass'), 'grass');
  assert.equal(fixCat('WS187_Sprague_field_paint_white_UNVERIFIED', 'grass'), '');
  assert.equal(fixCat('KX_drive_concrete', 'asphalt'), 'concrete');
  assert.equal(fixCat('Bark_Maple', ''), 'bark');
  assert.equal(fixCat('Roof_barrel_tile_course', ''), 'rooftile');
});

test('fence fabric and netting exported as glass are see-through metal', () => {
  assert.equal(fixCat('MH_chainlink_galv', 'glass'), 'metal');
  assert.equal(fixCat('fs_goal_net', 'glass'), 'metal');
  assert.equal(isSeeThroughSolid('MH_chainlink_galv', 'glass'), true);
  assert.equal(isSeeThroughSolid('SW_metal_chainlink_black', 'metal'), true);
});

test('window and lamp glass, and see-through materials without a category, stay glass', () => {
  assert.equal(isSeeThroughSolid('CELS_win_glass_thin', 'glass'), false);
  assert.equal(isSeeThroughSolid('Glass_Lamp_Frosted', 'glass'), false);
  assert.equal(isSeeThroughSolid('some_unnamed_clear_thing', ''), false);
});
