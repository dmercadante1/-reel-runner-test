// Fresh source proof in the pinned CI environment, alongside exact-candidate browser tests.
const fs=require('fs'),path=require('path'),{spawnSync}=require('child_process');
const engine=process.env.GODOT||'Godot_v4.7.2-stable_linux.x86_64';
function run(name,command,args){const result=spawnSync(command,args,{encoding:'utf8',maxBuffer:20*1024*1024,stdio:['ignore','pipe','pipe']});const log=String(result.stdout||'')+'\n'+String(result.stderr||'');fs.writeFileSync('godot/evidence/'+name+'.log',log);if(result.error)throw result.error;if(result.status!==0||/SCRIPT ERROR|Parse Error|^ERROR:/m.test(log))throw Error(name+' failed; inspect its log');}

if(!fs.existsSync('godot/assets/private-character/model.png'))throw Error('Approved production artwork missing from source');
run('chapter-native',engine,['--headless','--path','godot','--script','tests/chapter_smoke.gd']);
run('chapter-routes',engine,['--headless','--path','godot','--script','tests/chapter_routes.gd']);
for(const name of ['latest-chapter-results.json','latest-chapter-routes.json']){const result=JSON.parse(fs.readFileSync('godot/tests/'+name));if(result.failed)throw Error(name+' failed');fs.copyFileSync('godot/tests/'+name,'godot/evidence/'+name);}
run('chapter-source-export','python3',['godot/tools/export_chapter.py',engine,'build/chapter-source']);
fs.copyFileSync('build/chapter-source/manifest.json','godot/evidence/chapter-source-export.json');
