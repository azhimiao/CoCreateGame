// Local evidence housekeeping only; run after closing browser-session.cjs.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { PNG } = require('F:/beautiful/node_modules/pngjs');
const root = path.resolve(__dirname);
if (root.toLowerCase() !== path.resolve('F:/CoCreateGame/research/playthroughs/G04').toLowerCase()) throw Error('Unexpected root');
if (fs.existsSync(path.join(root, 'runtime'))) throw Error('Close browser and clean task runtime first');
const digest = data => crypto.createHash('sha256').update(data).digest('hex');
const logPath = path.join(root, 'operations.jsonl');
const raw = fs.readFileSync(logPath);
const rows = raw.toString('utf8').trim().split(/\r?\n/).map(JSON.parse);
if (!rows.some(r => r.event === 'runtime_cleanup' && r.removed === true)) throw Error('Missing cleanup confirmation');
let omittedFrames = 0, redactedUrls = 0;
function url(s) {
  if (typeof s !== 'string' || !s) return s;
  let value = s.split('?')[0].split('#')[0];
  value = value.replace(/(\/challenge-platform\/).*/, '$1[challenge-path-omitted]')
    .replace(/(\/user_id\/)[^/]+/g, '$1[identifier-omitted]');
  if (value !== s) redactedUrls++;
  return value;
}
for (const row of rows) {
  if (row.url) row.url = url(row.url);
  if (!row.frames) continue;
  for (const frame of row.frames) {
    if (!frame.url.startsWith('https://www.coolmathgames.com/')) {
      if (frame.visible_dom) { delete frame.visible_dom; frame.dom_omitted = 'Non-game auxiliary frame; no script/body excerpt retained'; omittedFrames++; }
    } else if (frame.visible_dom?.iframes) {
      for (const iframe of frame.visible_dom.iframes) iframe.src = url(iframe.src);
    }
    frame.url = url(frame.url);
  }
}
const sanitized = Buffer.from(rows.map(r => JSON.stringify(r)).join('\n') + '\n');
fs.writeFileSync(logPath, sanitized);
const screenshotRows = rows.filter(r => r.event === 'screenshot');
const shots = screenshotRows.map(row => {
  const target = path.resolve(root, row.file);
  if (!target.startsWith(path.join(root, 'screenshots') + path.sep)) throw Error('Unexpected screenshot path');
  const buffer = fs.readFileSync(target), png = PNG.sync.read(buffer), hash = digest(buffer);
  if (hash !== row.sha256) throw Error('Screenshot hash mismatch: ' + row.file);
  return { file:row.file, at:row.at, game:row.game, elapsed_ms:row.elapsed_ms, sha256:hash, bytes:buffer.length, width:png.width, height:png.height };
});
fs.writeFileSync(path.join(root,'screenshots','manifest.json'), JSON.stringify({ access_date:'2026-10-21', rights:'Third-party research evidence only; not original or licensed production assets', screenshots:shots }, null, 2) + '\n');
const games = rows.filter(r => r.event === 'navigation_start').map(start => {
  const input = rows.filter(r => r.game === start.game && r.event === 'input_start');
  const finish = rows.find(r => r.game === start.game && r.event === 'game_finished');
  return { game:start.game, official_url:start.official_url, started_at:start.at, administrative_finished_at:finish?.at,
    last_input_dispatched_at:input.at(-1)?.at, last_input_elapsed_ms:input.at(-1)?.elapsed_ms,
    dispatched_input_groups:input.length, status:finish?.status, effective_core_input_confirmed:rows.some(r => r.game === start.game && r.event === 'effective_game_input_confirmed_by_observer') };
});
fs.writeFileSync(path.join(root,'evidence-audit.json'), JSON.stringify({
  processed_at:new Date().toISOString(), operations_records:rows.length,
  log_processing:{ before_sha256:digest(raw), after_sha256:digest(sanitized), auxiliary_frame_dom_excerpts_omitted:omittedFrames, url_redactions:redactedUrls,
    retained:'All event timestamps, commands, screenshot hashes, errors and observer outcome statements remain unchanged.', raw_log_retained:false,
    reason:'Avoid retaining incidental auxiliary-frame scripts/challenge paths/analytics identifiers. No game source or extracted game asset is archived.' },
  games, screenshot_count:shots.length, screenshot_hashes_verified:true, runtime_exists:false,
  first_30_seconds_continuous_playthrough:'NOT_RECORDED', five_minutes_continuous_playthrough:'NOT_RECORDED',
  scope:'Only research/playthroughs/G04 written by this task; no games or benchmarks updates.'
}, null, 2) + '\n');
process.stdout.write(JSON.stringify({ games, screenshot_count:shots.length, screenshot_hashes_verified:true, runtime_exists:false, omittedFrames, redactedUrls }, null, 2) + '\n');
