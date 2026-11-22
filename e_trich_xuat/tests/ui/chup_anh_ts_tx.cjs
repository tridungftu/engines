// Công cụ QA: dùng Playwright đã có trên máy, không là dependency runtime.
const {chromium} = require(process.env.TX_PLAYWRIGHT || 'playwright');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
(async()=>{
  const browser=await chromium.launch({headless:true,timeout:20000});
  try {
    for(const [ten,width,height] of [['rong',1240,1460],['hep',420,1450]]) {
      const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
      await page.route(/^https?:/,route=>route.abort());
      const errors=[];page.on('pageerror',e=>errors.push(e.message));
      await page.goto(pathToFileURL(path.resolve('e_trich_xuat/docs/anh-ts-tx/DEMO-ts-tx.html')).href);
      await page.waitForSelector('html[data-da-nap="true"]',{state:'attached',timeout:15000});
      await page.screenshot({path:`e_trich_xuat/docs/anh-ts-tx/TS-TX-${ten}.png`,fullPage:true});
      console.log(JSON.stringify({ten,errors,rongTrang:await page.evaluate(()=>document.documentElement.scrollWidth),width}));
      await page.close();
    }
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
