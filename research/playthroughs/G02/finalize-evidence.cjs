// Run once after normal browser close; only task-directory outputs.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {PNG}=require('F:/beautiful/node_modules/pngjs');
const root=path.resolve(__dirname);
if(root.toLowerCase()!==path.resolve('F:/CoCreateGame/research/playthroughs/G02').toLowerCase())throw Error('Unexpected root');
if(fs.existsSync(path.join(root,'runtime')))throw Error('Close browser first; runtime still exists');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const file=path.join(root,'operations.jsonl'),raw=fs.readFileSync(file),rows=raw.toString('utf8').trim().split(/\r?\n/).map(JSON.parse);
if(!rows.some(r=>r.event==='runtime_cleanup'&&r.removed===true))throw Error('Missing normal cleanup confirmation');
let auxiliaryFrames=0,urlRedactions=0;
function clean(s){if(typeof s!=='string')return s;let out=s.split('?')[0].split('#')[0].replace(/&.*/,'');try{const u=new URL(out);if(!/playgama\.com$|crazygames\.com$/.test(u.hostname))out=u.origin+'/[auxiliary-path-omitted]';}catch{}if(out!==s)urlRedactions++;return out;}
for(const r of rows){if(r.url)r.url=clean(r.url);if(r.frames){const omitted=r.frames.filter(f=>f.dom_omitted);auxiliaryFrames+=omitted.length;r.auxiliary_frames_omitted=omitted.length;r.frames=r.frames.filter(f=>!f.dom_omitted);for(const f of r.frames){f.url=clean(f.url);if(f.ui?.iframes)for(const i of f.ui.iframes)i.src=clean(i.src);}}}
const processed=Buffer.from(rows.map(r=>JSON.stringify(r)).join('\n')+'\n');fs.writeFileSync(file,processed);
const shots=rows.filter(r=>r.event==='screenshot').map(r=>{const p=path.resolve(root,r.file);if(!p.startsWith(path.join(root,'screenshots')+path.sep))throw Error('Unsafe screenshot path');const b=fs.readFileSync(p),png=PNG.sync.read(b);if(hash(b)!==r.sha256)throw Error('Screenshot changed: '+r.file);return {file:r.file,at:r.at,game:r.game,attempt_elapsed_ms:r.attempt_elapsed_ms,game_elapsed_ms:r.game_elapsed_ms,sha256:r.sha256,bytes:b.length,width:png.width,height:png.height};});
fs.writeFileSync(path.join(root,'screenshots/manifest.json'),JSON.stringify({access_date:'2026-10-21',rights:'Third-party research evidence, not own production assets',screenshots:shots},null,2)+'\n');
const ready=rows.find(r=>r.event==='browser_ready');fs.writeFileSync(path.join(root,'device.json'),JSON.stringify({...ready,rendering_flags:['--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader'],continuous_recording:false,mobile_emulation:false,limitations:['Discrete screenshots only','Software renderer, no physical GPU performance result','Single desktop headless browser, no phone test','Fresh local profile, no login'],runtime_exists:false},null,2)+'\n');
const groups=rows.filter(r=>r.event==='input_start');
let md='# G02 浏览器操作索引\n\n访问日 2026-10-21。UTC 加 8 小时为北京时间；全部为离散截图。输入派发不等于游戏接受；逐节点判断见 observation.md。\n\n| UTC | 对象 | 实际派发命令 | 输入前截图 | 输入后截图 |\n| --- | --- | --- | --- | --- |\n';
for(const input of groups){const index=rows.indexOf(input),before=rows.slice(0,index).findLast(r=>r.event==='screenshot'&&r.game===input.game);let after=null;for(let i=index+1;i<rows.length;i++){if(rows[i].event==='input_start')break;if(rows[i].event==='screenshot'&&rows[i].game===input.game){after=rows[i];break;}}const link=r=>r?`[${path.basename(r.file)}](${r.file})`:'未取得';md+=`| ${input.at} | ${input.game} | \`${JSON.stringify(input.command).replace(/\|/g,'/')}\` | ${link(before)} | ${link(after)} |\n`;}
md+='\n页面错误、导航、观察者判断及清理事件均保留在 operations.jsonl。此索引按日志生成，不自动判断合法性、匹配、胜负或持续时长。\n';fs.writeFileSync(path.join(root,'operation-log.md'),md);
const benchmarkPath=path.resolve(root,'../../benchmarks/benchmarks.json');const currentBenchmarkHash=hash(fs.readFileSync(benchmarkPath));
const original='cfb4e1a53c79aca7999799aec7827c9b8423e8993a4f07464677438c590ec7bb';
const audit={processed_at:new Date().toISOString(),record_count:rows.length,screenshot_count:shots.length,screenshot_hashes_verified:true,input_groups:groups.length,
 log_processing:{before_sha256:hash(raw),after_sha256:hash(processed),auxiliary_frame_metadata_omitted:auxiliaryFrames,auxiliary_url_redactions:urlRedactions,raw_log_retained:false,retained:'Input commands, timestamps, official UI geometry, screenshot hashes, errors and observer statements unchanged'},
 original_benchmarks:{path:'research/benchmarks/benchmarks.json',initial_sha256:original,current_sha256:currentBenchmarkHash,unchanged:currentBenchmarkHash===original},
 runtime_exists:false,continuous_first_30_seconds:false,continuous_first_5_minutes:false,
 phases:rows.filter(r=>r.event==='navigation_start').map(start=>{const i=rows.indexOf(start),end=rows.slice(i+1).find(r=>r.session_id===start.session_id&&r.game===start.game&&['game_finished','attempt_cap_reached'].includes(r.event));return {game:start.game,session_id:start.session_id,started_at:start.at,ended_at:end?.at,end_event:end?.event,status:end?.status??'BLOCKED_AT_ATTEMPT_CAP',effective_core_input_confirmed:rows.slice(i,end?rows.indexOf(end)+1:undefined).some(r=>r.event==='effective_core_input_confirmed_by_observer')};}),
 final_assessment:JSON.parse(fs.readFileSync(path.join(root,'outcome-assessment.json'),'utf8')),
 scope:'Only research/playthroughs/G02 outputs; no games/reviews/benchmarks modifications by this task'};
fs.writeFileSync(path.join(root,'evidence-audit.json'),JSON.stringify(audit,null,2)+'\n');process.stdout.write(JSON.stringify(audit,null,2)+'\n');
