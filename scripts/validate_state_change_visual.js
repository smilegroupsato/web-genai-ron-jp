const fs = require('fs');
const {chromium} = require('playwright');
const names = ['index', ...Array.from({length:16},(_,i)=>`chapter-${String(i+1).padStart(2,'0')}`), 'bibliography'];
const output = '_state_change_visual_qa';
async function main() {
  fs.mkdirSync(output,{recursive:true});
  const browser = await chromium.launch({headless:true});
  const report = [];
  try {
    for (const width of [390,1440]) {
      const page=await browser.newPage({viewport:{width,height:900}});
      for (const name of names) {
        const path=`/article/state-change/${name==='index'?'':name+'.html'}`;
        const response=await page.goto(`http://127.0.0.1:8765/site${path}`,{waitUntil:'networkidle'});
        const value=await page.evaluate(()=>({
          author:document.querySelector('.author')?.textContent,
          canonical:document.querySelector('link[rel=canonical]')?.href,
          h1:document.querySelectorAll('h1').length,
          headings:[...document.querySelectorAll('h2')].map(e=>({id:e.id,text:e.textContent})),
          topLinks:[...document.querySelectorAll('.side-toc-link')].filter(e=>e.textContent.includes('論考①トップ')).map(e=>e.getAttribute('href')),
          overflow:document.documentElement.scrollWidth>innerWidth,
          width:innerWidth
        }));
        const errors=[];
        if(response.status()!==200) errors.push('HTTP response');
        if(value.author!=='著者：Taku｜生成AI論')errors.push('author');
        if(value.canonical!==`https://genai-ron.jp${path}`)errors.push('canonical');
        if(value.h1!==1)errors.push('h1');
        if(value.headings.some(h=>!h.id)||new Set(value.headings.map(h=>h.id)).size!==value.headings.length)errors.push('heading IDs');
        if(value.topLinks.length!==2||value.topLinks.some(h=>h!=='./'))errors.push('top links');
        if(value.overflow)errors.push('horizontal overflow');
        if(name==='index'||name==='chapter-05'||name==='bibliography') await page.screenshot({path:`${output}/${name}-${width}.png`,fullPage:false});
        report.push({name,width,...value,errors});
        if(errors.length)throw new Error(`${name}/${width}: ${errors.join(', ')}`);
      }
      await page.close();
    }
  } finally {
    fs.writeFileSync(`${output}/report.json`,JSON.stringify(report,null,2)+'\n');
    await browser.close();
  }
  console.log(`PASS: ${report.length} page/viewport cases`);
}
main().catch(e=>{console.error(e);process.exit(1)});
