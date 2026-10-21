// Local evidence-only browser check; no external assets or product deployment.
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
let playwright;
try { playwright = require('playwright-core'); }
catch { playwright = require(process.env.FOUNDRY_PLAYWRIGHT_MODULE || 'F:/beautiful/node_modules/playwright-core'); }
const root = path.resolve(__dirname, '..');
const cache = path.join(process.env.LOCALAPPDATA, 'ms-playwright');
function findExe(directory) {
  for (const item of fs.readdirSync(directory, { withFileTypes:true })) {
    const next = path.join(directory,item.name);
    if (item.isFile() && item.name === 'chrome-headless-shell.exe') return next;
    if (item.isDirectory()) { const found = findExe(next); if(found) return found; }
  }
}
(async()=>{
  const folder = fs.readdirSync(cache).filter(n=>n.startsWith('chromium_headless_shell-')).sort().pop();
  const browser = await playwright.chromium.launch({executablePath:findExe(path.join(cache,folder)),headless:true});
  const output = path.join(root,'validation','ui');
  fs.mkdirSync(output,{recursive:true});
  const results=[];
  try {
    for (const [width,height,label] of [[1440,1000,'desktop'],[768,1024,'tablet'],[390,844,'phone']]) {
      const page = await browser.newPage({viewport:{width,height}});
      const errors=[];
      page.on('pageerror',e=>errors.push(e.message));
      await page.goto(pathToFileURL(path.join(root,'index.html')).href);
      const initial = await page.locator('.project:visible').count();
      await page.locator('[data-filter="P0"]').click();
      const filtered = await page.locator('.project:visible').count();
      await page.locator('[data-filter="all"]').click();
      await page.locator('[data-doc="DELIVERY_REPORT.md"]').click();
      const modal = await page.locator('#reader').evaluate(e=>e.open);
      const textLength = (await page.locator('#doc-content').textContent()).length;
      await page.locator('#close-reader').click();
      const metrics = await page.evaluate(()=>({
        horizontalOverflow:document.documentElement.scrollWidth>window.innerWidth,
        missingEmbeddedDocuments:[...document.querySelectorAll('[data-doc]')].filter(a=>!JSON.parse(document.getElementById('documents').textContent)[a.dataset.doc]).map(a=>a.dataset.doc)
      }));
      const localHrefs = await page.locator('a[href]').evaluateAll(nodes=>nodes.map(a=>a.getAttribute('href')).filter(h=>h && !/^(https?:|#|mailto:)/i.test(h)));
      metrics.missingLocalLinks = localHrefs.filter(h=>!fs.existsSync(path.resolve(root,decodeURIComponent(h.split('#')[0]))));
      await page.screenshot({path:path.join(output,label+'.png'),fullPage:true});
      const result={viewport:{width,height},initialProjects:initial,filteredProjects:filtered,modalOpened:modal,modalTextLength:textLength,...metrics,pageErrors:errors};
      result.result = initial===10 && filtered===3 && modal && textLength>500 && !metrics.horizontalOverflow && !errors.length && !metrics.missingEmbeddedDocuments.length && !metrics.missingLocalLinks.length ? 'PASS' : 'FAIL';
      results.push(result);
      await page.close();
    }
  } finally { await browser.close(); }
  fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({scope:'OFFLINE_DOCUMENT_INDEX_ONLY',results},null,2)+'\n');
  console.log(JSON.stringify(results));
  if(results.some(r=>r.result!=='PASS')) process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
