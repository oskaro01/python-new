(function () {
  'use strict';
  const M = window.EvidenceModel;
  const MAX_BACKUP = 70 * 1024 * 1024;
  function download(blob, name) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = name; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  }
  const filename = title => (title.replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').slice(0, 100) || 'Evidence workbook');
  function dataURL(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader(); reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error('Could not read screenshot.')); reader.readAsDataURL(blob);
    });
  }
  async function excel(project, schema, images) {
    const book = new ExcelJS.Workbook();
    book.creator = 'Evidence Desk'; book.created = new Date();
    const names = new Set();
    function sheet(title, wide = false) {
      const base = title.replace(/[\[\]:*?/\\]/g, ' ').replace(/^'+|'+$/g, '').trim().slice(0, 27) || 'Section';
      let name = base; let n = 1;
      while (names.has(name.toLowerCase())) name = `${base} ${++n}`;
      names.add(name.toLowerCase());
      const page = book.addWorksheet(name, {pageSetup: {paperSize: 9, orientation: wide ? 'landscape' : 'portrait', fitToPage: true, fitToWidth: 1, fitToHeight: 0}});
      page.views = [{state: 'frozen', ySplit: 2}];
      page.columns = Array.from({length: 10}, (_, i) => ({width: i === 0 ? 29 : 33}));
      return page;
    }
    function row(page, cells, heading = false) {
      const added = page.addRow(cells.map(value => String(value ?? '')));
      added.eachCell(cell => {
        cell.font = {name: 'Calibri', size: 11, ...(heading ? {bold: true, color: {argb: 'FFFFFFFF'}} : {})};
        cell.alignment = {vertical: 'top', wrapText: true};
        if (heading) cell.fill = {type: 'pattern', pattern: 'solid', fgColor: {argb: 'FF285E61'}};
      });
      const lines = Math.max(1, ...cells.map(value => String(value ?? '').split('\n').reduce((sum, line) => sum + Math.max(1, Math.ceil(line.length / 34)), 0)));
      added.height = Math.min(390, Math.max(23, lines * 15));
      return added;
    }
    const overview = sheet('Workbook');
    row(overview, [schema.title], true);
    row(overview, ['Exported', new Date().toISOString()]);
    Object.entries(schema.metadata).forEach(([key, value]) => row(overview, [key, value]));
    row(overview, ['Section', 'Status', 'Screenshots'], true);
    for (const section of schema.sections) row(overview, [section.title, project.statuses[section.id] || 'Not started', images.filter(image => image.sectionId === section.id).length]);
    const evidence = sheet('Evidence', true);
    row(evidence, ['Evidence', 'Section / Entry', 'Caption', 'Source', 'Captured', 'Screenshot'], true);
    evidence.getColumn(6).width = 62;
    for (const image of images) {
      const section = schema.sections.find(section => section.id === image.sectionId);
      const added = row(evidence, [image.label, `${section?.title || 'Previous template section'}\n${image.contextLabel}`, image.caption, image.source, image.createdAt, '']);
      const scale = Math.min(420 / image.width, 300 / image.height, 1);
      const width = image.width * scale, height = image.height * scale;
      added.height = Math.max(added.height, (height + 12) * 0.75);
      const id = book.addImage({base64: await dataURL(image.blob), extension: image.extension});
      evidence.addImage(id, {tl: {col: 5.05, row: added.number - 0.95}, ext: {width, height}, editAs: 'oneCell'});
    }
    const refs = id => images.filter(image => image.contextId === id).map(image => image.label).join(', ');
    for (const section of schema.sections) {
      const page = sheet(section.title, true);
      row(page, [section.title], true);
      row(page, ['Status', project.statuses[section.id] || 'Not started']);
      for (const block of section.blocks) {
        if (block.type === 'prose') {
          const text = M.plain(block.markdown);
          // Split long prose so Excel's cell-length limit cannot truncate the source silently.
          for (let start = 0; start < text.length; start += 30000) {
            const added = row(page, [text.slice(start, start + 30000)]);
            page.mergeCells(added.number, 1, added.number, 6);
          }
        }
        if (block.type === 'table') {
          const rows = M.filledRows(project, block);
          if (block.kind === 'pivot') {
            row(page, block.headers, true); rows.forEach(cells => row(page, cells));
            row(page, ['Evidence', ...block.items.map(item => refs(item.id))]);
          } else {
            row(page, [...block.headers, 'Evidence'], true);
            rows.forEach((cells, index) => row(page, [...cells, refs(block.items[index].id)]));
          }
          page.addRow([]);
        }
        if (block.type === 'notes') row(page, [block.item.label, M.value(project, block.item.fields[0]), refs(block.item.id)]);
        if (block.type === 'checklist') for (const item of block.items) row(page, [item.id ? M.checked(project, item) ? 'Done' : 'Pending' : '', item.label || item.text]);
      }
      if (refs(section.id)) row(page, ['Section evidence', refs(section.id)]);
    }
    const old = M.unmatched(project, schema);
    if (old.length) {
      const page = sheet('Answers needing review');
      row(page, ['Previous field', 'Saved answer'], true);
      old.forEach(([key, value]) => row(page, [project.catalog[key]?.label || key, value]));
    }
    return new Blob([await book.xlsx.writeBuffer()], {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
  }
  async function backup(project, schema, images) {
    const files = {};
    const metadata = images.map(({blob, ...image}) => image);
    files['project.json'] = fflate.strToU8(JSON.stringify({format: 'evidence-desk', version: 1, project, images: metadata}));
    files['template.md'] = fflate.strToU8(project.markdown);
    files['report.md'] = fflate.strToU8(M.report(project, schema, images));
    for (const image of images) files[`images/${image.id}.${image.extension}`] = new Uint8Array(await image.blob.arrayBuffer());
    return new Blob([fflate.zipSync(files, {level: 0})], {type: 'application/zip'});
  }
  async function restore(file) {
    if (file.size > MAX_BACKUP) throw new Error('Backup is too large (70 MB maximum).');
    let total = 0, count = 0;
    const files = fflate.unzipSync(new Uint8Array(await file.arrayBuffer()), {filter: entry => {
      total += entry.originalSize; count++;
      if (!Number.isFinite(total) || total > MAX_BACKUP || count > 110 || entry.originalSize > MAX_BACKUP) throw new Error('Backup exceeds safe extraction limits.');
      return true;
    }});
    if (!files['project.json'] || files['project.json'].length > 3000000) throw new Error('Not an Evidence Desk backup.');
    const data = JSON.parse(fflate.strFromU8(files['project.json']));
    if (data.format !== 'evidence-desk' || data.version !== 1 || !data.project || !Array.isArray(data.images) || data.images.length > 100) throw new Error('Unsupported backup format.');
    const source = data.project;
    const project = M.create(source.markdown, String(source.filename || 'Restored.md'), crypto.randomUUID());
    project.title += ' (restored)';
    function record(value, type) {
      if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid saved answers.');
      return Object.fromEntries(Object.entries(value).map(([key, value]) => {
        if (key.length > 500 || typeof value !== type || (type === 'string' && value.length > 30000)) throw new Error('Invalid saved answer.');
        return [key, value];
      }));
    }
    project.values = record(source.values, 'string'); project.checks = record(source.checks, 'boolean');
    project.statuses = record(source.statuses, 'string');
    if (Object.values(project.statuses).some(status => !M.STATUSES.includes(status))) throw new Error('Invalid section status.');
    // Only copy known catalog properties; backup data never becomes HTML or executable code.
    for (const [key, entry] of Object.entries(source.catalog || {})) {
      if (['__proto__', 'constructor', 'prototype'].includes(key) || key.length > 500 || !entry || typeof entry !== 'object') continue;
      project.catalog[key] = {label: String(entry.label || '').slice(0, 500), sectionId: String(entry.sectionId || '').slice(0, 500), itemLabel: String(entry.itemLabel || '').slice(0, 500)};
    }
    const images = [];
    for (const image of data.images) {
      if (!/^[a-zA-Z0-9-]{1,80}$/.test(image.id) || !['png', 'jpeg'].includes(image.extension)) throw new Error('Invalid screenshot record.');
      const bytes = files[`images/${image.id}.${image.extension}`];
      if (!bytes || bytes.length > 5 * 1024 * 1024) throw new Error('Screenshot is missing or exceeds 5 MB.');
      const blob = new Blob([bytes], {type: `image/${image.extension}`});
      const decoded = await createImageBitmap(blob);
      const width = decoded.width, height = decoded.height; decoded.close();
      if (width * height > 16000000) throw new Error('Screenshot dimensions are too large.');
      const text = key => String(image[key] || '').slice(0, 2000);
      images.push({id: crypto.randomUUID(), projectId: project.id, label: text('label'), sectionId: text('sectionId'), contextId: text('contextId'), contextLabel: text('contextLabel'), caption: text('caption'), source: text('source'), createdAt: text('createdAt'), extension: image.extension, blob, width, height});
    }
    return {project, images};
  }
  window.EvidenceExports = {download, filename, excel, backup, restore};
})();
