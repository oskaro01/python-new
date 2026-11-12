const {copyFileSync, mkdirSync} = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const destination = path.join(root, 'vendor');
mkdirSync(destination, {recursive: true});
for (const [source, name] of [
  ['marked/lib/marked.umd.js', 'marked.js'],
  ['dompurify/dist/purify.min.js', 'purify.js'],
  ['exceljs/dist/exceljs.min.js', 'exceljs.js'],
  ['fflate/umd/index.js', 'fflate.js'],
  ['marked/LICENSE.md', 'marked-LICENSE.md'],
  ['dompurify/LICENSE', 'dompurify-LICENSE'],
  ['exceljs/LICENSE', 'exceljs-LICENSE'],
  ['fflate/LICENSE', 'fflate-LICENSE'],
]) copyFileSync(path.join(root, 'node_modules', source), path.join(destination, name));
console.log('Local browser libraries and licenses copied.');
