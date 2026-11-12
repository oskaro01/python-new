(function () {
  'use strict';
  const M = EvidenceModel, S = EvidenceStore, X = EvidenceExports;
  const $ = id => document.getElementById(id);
  let project = null, schema = null, images = [], projects = [], sectionId = '', updating = false;
  let saveTimer, toastTimer, saveChain = Promise.resolve(), uploadContext = null, busy = false;
  const urls = new Map();
  function el(tag, className, text) {
    const node = document.createElement(tag); if (className) node.className = className;
    if (text !== undefined) node.textContent = text; return node;
  }
  function toast(message) {
    $('toast').textContent = message; $('toast').hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => { $('toast').hidden = true; }, 5500);
  }
  function url(image) {
    if (!urls.has(image.id)) urls.set(image.id, URL.createObjectURL(image.blob));
    return urls.get(image.id);
  }
  function forgetURLs() { for (const value of urls.values()) URL.revokeObjectURL(value); urls.clear(); }
  function touch() {
    project.updatedAt = new Date().toISOString(); $('save-status').textContent = 'Saving...';
    clearTimeout(saveTimer); saveTimer = setTimeout(() => flush().catch(error => toast(error.message)), 450);
  }
  async function flush() {
    clearTimeout(saveTimer);
    if (!project) return;
    const snapshot = structuredClone(project), screenshots = [...images];
    const operation = saveChain.catch(() => {}).then(async () => {
      await S.restore(snapshot, screenshots);
      if (project?.id === snapshot.id && project.updatedAt === snapshot.updatedAt) $('save-status').textContent = 'Saved on this device';
    });
    saveChain = operation;
    try { await operation; } catch (error) { $('save-status').textContent = 'Save failed'; throw new Error(`Could not save locally: ${error.message}`); }
  }
  function markdown(text) {
    const node = el('div', 'prose');
    node.innerHTML = DOMPurify.sanitize(marked.parse(text), {USE_PROFILES: {html: true}, FORBID_TAGS: ['img', 'style', 'input', 'form', 'iframe', 'video', 'audio', 'link', 'source', 'object', 'embed'], FORBID_ATTR: ['style']});
    node.querySelectorAll('a').forEach(link => { link.target = '_blank'; link.rel = 'noopener noreferrer'; });
    return node;
  }
  async function refreshProjects() {
    projects = await S.getProjects();
    $('project-select').replaceChildren();
    if (!projects.length) $('project-select').append(new Option('No workbooks', ''));
    for (const item of projects) $('project-select').append(new Option(item.title, item.id));
    if (project) $('project-select').value = project.id;
  }
  async function open(id, preferred, saveCurrent = true) {
    if (saveCurrent) await flush();
    project = (await S.getProjects()).find(item => item.id === id) || null;
    forgetURLs(); images = project ? await S.getImages(id) : [];
    schema = project ? M.parse(project.markdown, project.filename) : null;
    sectionId = preferred || schema?.sections.find(section => section.items.length)?.id || schema?.sections[0].id || '';
    try { localStorage.setItem('evidence-desk-active', id || ''); } catch (_) { /* IndexedDB still stores the workbook. */ }
    await refreshProjects(); render();
  }
  function nav() {
    $('sections').replaceChildren();
    if (!schema) return;
    const query = $('section-search').value.trim().toLowerCase();
    for (const section of schema.sections.filter(section => section.title.toLowerCase().includes(query) || section.path.includes(query))) {
      const button = el('button', `${section.id === sectionId ? 'active ' : ''}${section.depth <= 2 ? 'part' : ''}`);
      const status = project.statuses[section.id] || 'Not started';
      button.append(el('span', `status-dot ${status === 'Complete' ? 'complete' : status === 'In progress' ? 'progress' : ''}`), el('span', '', section.title));
      button.title = `${section.title}: ${status}`;
      button.onclick = () => { sectionId = section.id; renderSection(); nav(); document.body.classList.remove('mobile-nav'); };
      $('sections').append(button);
    }
    $('section-count').textContent = schema.sections.length;
    const completed = schema.sections.filter(section => project.statuses[section.id] === 'Complete').length;
    $('progress-label').textContent = `${completed} / ${schema.sections.length} complete`;
  }
  function review() {
    const entries = M.unmatched(project, schema);
    const ids = new Set(schema.sections.flatMap(section => [section.id, ...section.items.map(item => item.id)]));
    const oldImages = images.filter(image => !ids.has(image.contextId));
    const banner = $('review-banner'); banner.replaceChildren(); banner.hidden = !entries.length && !oldImages.length;
    if (banner.hidden) return;
    banner.append(el('strong', '', 'Previous template data retained for review'));
    if (entries.length) {
      const details = el('details'), list = el('ul'); details.append(el('summary', '', `${entries.length} saved answers no longer match a field`));
      entries.forEach(([key, value]) => list.append(el('li', '', `${project.catalog[key]?.label || key}: ${String(value)}`)));
      details.append(list); banner.append(details);
    }
    if (oldImages.length) {
      banner.append(el('p', '', `${oldImages.length} screenshots belong to changed or removed entries.`));
      banner.append(imageGrid(oldImages));
    }
  }
  function command(label, icon, handler, iconOnly = false) {
    const button = el('button', iconOnly ? 'icon-button' : ''); button.type = 'button'; button.title = label; button.setAttribute('aria-label', label);
    if (icon) { const img = el('img'); img.src = `assets/icons/${icon}.svg`; img.alt = ''; button.append(img); }
    if (!iconOnly) button.append(document.createTextNode(label)); button.onclick = handler; return button;
  }
  function imageGrid(entries) {
    const grid = el('div', 'evidence-grid');
    for (const image of entries) {
      const card = el('div', 'evidence-item');
      const preview = el('button', 'evidence-image'); preview.title = `Preview ${image.label}`; preview.setAttribute('aria-label', preview.title);
      const img = el('img'); img.src = url(image); img.alt = image.caption || `${image.label}: ${image.contextLabel}`;
      preview.append(img); preview.onclick = () => {
        $('image-preview').querySelector('img').src = url(image);
        $('image-preview').querySelector('p').textContent = `${image.label} - ${image.caption || image.contextLabel}`;
        $('image-preview').showModal();
      };
      const info = el('div', 'evidence-meta'), actions = el('div', 'evidence-label');
      actions.append(el('strong', '', image.label), command('Download screenshot', 'download', () => X.download(image.blob, `${image.label}.${image.extension}`), true), command('Remove screenshot', 'trash-2', () => run(async () => {
        if (!confirm(`Delete screenshot ${image.label}?`)) return;
        await flush(); await S.removeImage(image.id); images = images.filter(item => item.id !== image.id);
        if (urls.has(image.id)) { URL.revokeObjectURL(urls.get(image.id)); urls.delete(image.id); }
        touch(); renderSection(); review();
      }), true));
      info.append(actions);
      for (const [key, placeholder] of [['caption', 'Caption'], ['source', 'Source URL or reference']]) {
        const input = el('input'); input.type = 'text'; input.placeholder = placeholder; input.maxLength = 2000;
        input.value = image[key]; input.setAttribute('aria-label', `${image.label} ${placeholder}`);
        input.oninput = () => { image[key] = input.value; touch(); }; info.append(input);
      }
      card.append(preview, info); grid.append(card);
    }
    return grid;
  }
  function evidence(contextId, contextLabel) {
    const area = el('div', 'evidence-block'); area.dataset.context = contextId; area.dataset.contextLabel = contextLabel;
    const toolbar = el('div', 'evidence-toolbar');
    toolbar.append(el('span', '', 'Evidence'), command('Add screenshot', 'plus', () => {
      uploadContext = {id: contextId, label: contextLabel, sectionId}; $('image-file').click();
    }));
    area.append(toolbar, imageGrid(images.filter(image => image.contextId === contextId))); return area;
  }
  function entry(item, expanded) {
    const details = el('details', 'entry'); details.open = expanded; details.dataset.context = item.id; details.dataset.contextLabel = item.label;
    details.append(el('summary', '', item.label));
    const fields = el('div', `fields${item.fields.length === 1 ? ' single' : ''}`);
    for (const field of item.fields) {
      const label = el('label', 'field'); label.append(el('span', '', field.label));
      const input = el('textarea'); input.rows = item.fields.length === 1 ? 2 : 3; input.maxLength = 30000;
      input.dataset.fieldId = field.id; input.value = M.value(project, field); input.dir = 'auto';
      input.oninput = () => { project.values[field.id] = input.value; touch(); };
      label.append(input); fields.append(label);
    }
    const body = el('div', 'entry-body'); body.append(fields, evidence(item.id, item.label));
    details.append(body); return details;
  }
  function renderSection() {
    if (!schema) return;
    const section = schema.sections.find(section => section.id === sectionId) || schema.sections[0]; sectionId = section.id;
    $('section-path').textContent = section.path.split('/').slice(0, -1).join(' / ');
    $('section-title').textContent = section.title;
    $('section-status').value = project.statuses[sectionId] || 'Not started';
    const content = $('section-content');
    const expanded = new Map([...content.querySelectorAll('details.entry')].map(node => [node.dataset.context, node.open]));
    content.replaceChildren();
    for (const block of section.blocks) {
      if (block.type === 'prose') content.append(markdown(block.markdown));
      if (block.type === 'table') block.items.forEach((item, index) => content.append(entry(item, expanded.get(item.id) ?? (block.kind === 'keyValue' || index === 0))));
      if (block.type === 'notes') content.append(entry(block.item, true));
      if (block.type === 'checklist') {
        const list = el('div', 'checklist');
        for (const item of block.items) {
          const label = el('label');
          if (item.id) { const input = el('input'); input.type = 'checkbox'; input.checked = M.checked(project, item); input.onchange = () => { project.checks[item.id] = input.checked; touch(); }; label.append(input); }
          label.append(document.createTextNode(item.label || item.text)); list.append(label);
        }
        content.append(list);
      }
    }
    $('section-evidence').replaceChildren(evidence(sectionId, section.title));
    $('evidence-count').textContent = `${images.length} screenshot${images.length === 1 ? '' : 's'}`;
  }
  function render() {
    $('empty-state').hidden = !!project; $('workbook').hidden = !project;
    for (const id of ['update-md', 'backup', 'delete-project', 'export-xlsx', 'print']) $(id).disabled = !project;
    if (!project) { $('sections').replaceChildren(); $('section-count').textContent = '0'; $('evidence-count').textContent = '0 screenshots'; $('save-status').textContent = 'Ready'; return; }
    $('product-title').textContent = project.title; $('document-label').textContent = project.filename;
    $('save-status').textContent = 'Saved on this device'; nav(); review(); renderSection();
  }
  async function importMarkdown(text, name) {
    await flush();
    const next = updating && project ? M.revise(project, text, name) : M.create(text, name, crypto.randomUUID());
    await S.save(next); const preferred = updating ? sectionId : undefined;
    await open(next.id, preferred, false); toast(updating ? 'Template updated. Existing answers retained.' : 'Workbook imported.');
  }
  async function addImages(files, context) {
    if (!project || !context) return;
    if (files.length + images.length > 100) throw new Error('Keep each workbook to 100 screenshots or fewer.');
    let total = images.reduce((sum, image) => sum + image.blob.size, 0);
    for (const file of files) {
      if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) throw new Error('Use PNG, JPEG or WebP images.');
      if (file.size > 5 * 1024 * 1024) throw new Error('Each screenshot must be 5 MB or smaller.');
      const bitmap = await createImageBitmap(file);
      const width = bitmap.width, height = bitmap.height;
      if (width * height > 16000000) { bitmap.close(); throw new Error('Keep screenshot dimensions below 16 megapixels.'); }
      let blob = file, extension = file.type === 'image/jpeg' ? 'jpeg' : 'png';
      if (file.type === 'image/webp') {
        const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
        canvas.getContext('2d').drawImage(bitmap, 0, 0);
        blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
        if (!blob) { bitmap.close(); throw new Error('Could not convert screenshot.'); }
      }
      bitmap.close(); total += blob.size;
      if (blob.size > 5 * 1024 * 1024 || total > 60 * 1024 * 1024) throw new Error('Screenshot storage limit reached (5 MB each, 60 MB per workbook).');
      const number = Math.max(0, ...images.map(image => Number(image.label.match(/\d+$/)?.[0]) || 0)) + 1;
      const image = {id: crypto.randomUUID(), projectId: project.id, sectionId: context.sectionId, contextId: context.id, contextLabel: context.label, label: `E-${String(number).padStart(3, '0')}`, caption: '', source: '', createdAt: new Date().toISOString(), width, height, extension, blob};
      await S.putImage(image); images.push(image); touch();
    }
    renderSection(); review(); toast('Screenshot saved.');
  }
  async function run(action) {
    if (busy) return;
    busy = true; document.body.classList.add('busy');
    try { await action(); } catch (error) { console.error(error); toast(error.message || 'Something went wrong.'); }
    finally { busy = false; document.body.classList.remove('busy'); }
  }
  function selectFile(update) { updating = update; $('md-file').click(); }
  $('import-md').onclick = $('empty-import').onclick = () => selectFile(false);
  $('update-md').onclick = () => selectFile(true);
  $('md-file').onchange = event => run(async () => {
    const file = event.target.files[0]; event.target.value = ''; if (!file) return;
    if (file.size > 500000) throw new Error('Markdown files must be 500 KB or smaller.');
    await importMarkdown(await file.text(), file.name);
  });
  $('image-file').onchange = event => {
    const files = [...event.target.files]; event.target.value = '';
    run(() => addImages(files, uploadContext));
  };
  document.addEventListener('paste', event => {
    if (!project || busy || $('image-preview').open) return;
    const files = [...(event.clipboardData?.items || [])].filter(item => item.kind === 'file' && item.type.startsWith('image/')).map(item => item.getAsFile()).filter(Boolean);
    if (!files.length) return;
    event.preventDefault();
    const node = event.target.closest('[data-context]');
    const section = schema.sections.find(section => section.id === sectionId);
    run(() => addImages(files, {id: node?.dataset.context || sectionId, label: node?.dataset.contextLabel || section.title, sectionId}));
  });
  $('project-select').onchange = event => run(() => open(event.target.value));
  $('section-search').oninput = nav;
  $('section-status').onchange = event => { project.statuses[sectionId] = event.target.value; touch(); nav(); };
  M.STATUSES.forEach(status => $('section-status').append(new Option(status, status)));
  $('export-xlsx').onclick = () => run(async () => {
    $('save-status').textContent = 'Building Excel workbook...'; await flush();
    const snapshot = structuredClone(project);
    const blob = await X.excel(snapshot, schema, structuredClone(images)); X.download(blob, `${X.filename(snapshot.title)}.xlsx`);
    $('save-status').textContent = 'Saved on this device'; toast('Excel workbook exported.');
  });
  $('backup').onclick = () => run(async () => { await flush(); const snapshot = structuredClone(project); X.download(await X.backup(snapshot, schema, structuredClone(images)), `${X.filename(snapshot.title)}-backup.zip`); toast('Backup exported.'); });
  $('restore').onclick = () => $('backup-file').click();
  $('backup-file').onchange = event => run(async () => {
    const file = event.target.files[0]; event.target.value = ''; if (!file) return;
    await flush(); const restored = await X.restore(file); await S.restore(restored.project, restored.images);
    await open(restored.project.id); toast('Backup restored as a separate workbook.');
  });
  $('delete-project').onclick = () => run(async () => {
    if (!confirm(`Delete "${project.title}" and its screenshots from this browser?`)) return;
    await flush(); await S.removeProject(project.id); project = null;
    const remaining = await S.getProjects(); await open(remaining[0]?.id || '');
  });
  $('toggle-nav').onclick = () => document.body.classList.toggle(matchMedia('(max-width:620px)').matches ? 'mobile-nav' : 'nav-hidden');
  $('close-preview').onclick = () => $('image-preview').close();
  $('image-preview').onclick = event => { if (event.target === $('image-preview')) $('image-preview').close(); };
  $('print').onclick = () => run(async () => {
    await flush(); const report = el('div', 'print-report'); report.id = 'print-report';
    report.append(markdown(M.report(project, schema, images)));
    for (const image of images) {
      const figure = el('figure'); figure.append(el('figcaption', '', `${image.label} - ${image.contextLabel}`));
      const img = el('img'); img.src = url(image); img.alt = image.caption; figure.append(img); report.append(figure);
    }
    document.body.append(report);
    await Promise.all([...report.querySelectorAll('img')].map(img => img.decode().catch(() => {})));
    window.print(); report.remove();
  });
  $('load-example').onclick = () => run(async () => { updating = false; await importMarkdown(SAMPLE, 'Sample evidence pack.md'); });
  window.addEventListener('beforeunload', event => {
    if ($('save-status').textContent === 'Saving...' || busy) { event.preventDefault(); event.returnValue = ''; }
  });
  const SAMPLE = '# Product research return sheet\n\n**Product:** Sample air duster\n**Research date:** 12 November 2026\n\n## Business inputs\n\n| Required input | Your answer |\n| --- | --- |\n| Target selling price | |\n| Shipping cost | |\n\n## Market evidence\n\n| Country | Language | Search phrase | Observations |\n| --- | --- | --- | --- |\n| UAE | English | cordless air duster | |\n| Saudi Arabia | Arabic | منفاخ هواء | |\n\n## Creator videos\n\n| Field | Video 1 | Video 2 |\n| --- | --- | --- |\n| Creator | | |\n| URL | | |\n| Main claim | | |\n\n## Completion\n\n- [ ] Sources recorded\n- [ ] Screenshots attached\n\n**Additional observations:**\n\n[Write here]\n';
  window.EvidenceDesk = {getState: () => ({project, schema, images}), ready: (async () => {
    try {
      projects = await S.getProjects(); let last;
      try { last = localStorage.getItem('evidence-desk-active'); } catch (_) { /* Storage preference is optional. */ }
      await open(projects.find(item => item.id === last)?.id || projects[0]?.id || '');
    } catch (error) { $('save-status').textContent = 'Storage unavailable'; toast(`Browser storage is unavailable: ${error.message}`); }
  })()};
})();
