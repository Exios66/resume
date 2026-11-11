// Full-page captures of the real status page, light and dark, while one real job runs.
// Usage: node capture.cjs <out-dir> [interval-ms] [frames-after-exit]
// MR_CHECKOUT names the MapReduce-Reloaded checkout (default: /home/user/exios66/mapreduce-reloaded).
const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
const out=process.argv[2], every=+process.argv[3]||1500, hold=+process.argv[4]||6, MAX_FRAMES=600;
const checkout=process.env.MR_CHECKOUT||'/home/user/exios66/mapreduce-reloaded';
if(!out){console.error('usage: node capture.cjs <out-dir> [interval-ms] [frames-after-exit]');process.exit(2);}
fs.mkdirSync(`${out}/frames`,{recursive:true});
(async()=>{const b=await chromium.launch();
 const pages={};for(const m of ['light','dark']){pages[m]=await b.newPage({viewport:{width:1200,height:760},deviceScaleFactor:2,colorScheme:m});await pages[m].goto('http://127.0.0.1:18780/');}
 const t0=Date.now();
 const job=spawn('bin/mr',['submit','-coordinator','127.0.0.1:7070','-m','32','-r','4','-wait','examples/wordcount.go','/data/out/capture-wc-1g','/data/input/capture-1g/access.log'],{cwd:checkout,env:{...process.env,MR_DATA_DIR:'/data'}});
 let done=false,code=null,log='';job.stdout.on('data',d=>log+=d);job.stderr.on('data',d=>log+=d);
 job.on('error',e=>{done=true;code=-1;log+=`\nspawn error ${e.message}\n`;});
 job.on('exit',c=>{done=true;code=c;log+=`\nexit ${c}\n`;});
 let n=0,after=0,truncated=false;
 while(true){const tick=Date.now();
  for(const m of ['light','dark']){await pages[m].reload({waitUntil:'load'});await pages[m].screenshot({path:`${out}/frames/${m}-${String(n).padStart(3,'0')}.png`,fullPage:true});}
  fs.appendFileSync(`${out}/frames.tsv`,`${n}\t${((tick-t0)/1000).toFixed(2)}\n`);n++;
  if(done){after++;if(after>=hold)break;}
  if(n>=MAX_FRAMES){truncated=true;break;}
  const wait=every-(Date.now()-tick);if(wait>0)await new Promise(r=>setTimeout(r,wait));}
 if(truncated){log+=`\nINCOMPLETE: stopped after ${MAX_FRAMES} frames while the job was still running\n`;job.kill();}
 fs.writeFileSync(`${out}/submit.log`,log);console.log('frames',n,'seconds',((Date.now()-t0)/1000).toFixed(1));await b.close();
 if(truncated){console.error('capture incomplete: frame limit reached');process.exitCode=3;}
 else if(code!==0){console.error(`job failed: exit ${code}`);process.exitCode=1;}})();
