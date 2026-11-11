// Full-page captures of the real status page, light and dark, while one real job runs.
const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
const out=process.argv[2], every=+process.argv[3]||1500, hold=+process.argv[4]||6;
(async()=>{const b=await chromium.launch();
 const pages={};for(const m of ['light','dark']){pages[m]=await b.newPage({viewport:{width:1200,height:760},deviceScaleFactor:2,colorScheme:m});await pages[m].goto('http://127.0.0.1:18780/');}
 const t0=Date.now();
 const job=spawn('bin/mr',['submit','-coordinator','127.0.0.1:7070','-m','32','-r','4','-wait','examples/wordcount.go','/data/out/capture-wc-1g','/data/input/capture-1g/access.log'],{cwd:'/home/user/exios66/mapreduce-reloaded',env:{...process.env,MR_DATA_DIR:'/data'}});
 let done=false,log='';job.stdout.on('data',d=>log+=d);job.stderr.on('data',d=>log+=d);job.on('exit',c=>{done=true;log+=`\nexit ${c}\n`;});
 let n=0,after=0;
 while(true){const tick=Date.now();
  for(const m of ['light','dark']){await pages[m].reload({waitUntil:'load'});await pages[m].screenshot({path:`${out}/frames/${m}-${String(n).padStart(3,'0')}.png`,fullPage:true});}
  fs.appendFileSync(`${out}/frames.tsv`,`${n}\t${((tick-t0)/1000).toFixed(2)}\n`);n++;
  if(done){after++;if(after>=hold)break;}
  const wait=every-(Date.now()-tick);if(wait>0)await new Promise(r=>setTimeout(r,wait));
  if(n>600)break;}
 fs.writeFileSync(`${out}/submit.log`,log);console.log('frames',n,'seconds',((Date.now()-t0)/1000).toFixed(1));await b.close();})();
