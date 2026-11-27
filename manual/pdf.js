// Render manual/index.html to a Letter PDF with an ESC footer and page numbers.
// Usage: node manual/pdf.js <out.pdf> <issue text>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const out = process.argv[2];
  const issue = process.argv[3] || '';
  const b = await chromium.launch();
  const p = await b.newPage({ colorScheme: 'light' });
  await p.goto('file://' + path.resolve(__dirname, 'index.html'), { waitUntil: 'load' });
  await p.emulateMedia({ media: 'print', colorScheme: 'light' });
  await p.pdf({
    path: out,
    format: 'Letter',
    printBackground: true,
    outline: true,
    tagged: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate:
      '<div style="width:100%;font:8px Arial,Helvetica,sans-serif;color:#474747;padding:0 0.6in;display:flex;justify-content:space-between">' +
      '<span>Emory Street Construction · ESC-MAN-01 Building Manual · ' + issue.replace(/[<>&]/g, '') + '</span>' +
      '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '0.6in', bottom: '0.7in', left: '0.6in', right: '0.6in' },
  });
  await b.close();
})();
