(function (root, factory) {
  const api = factory(root.marked || require('./vendor/marked.js').marked);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.EvidenceModel = api;
})(globalThis, function (marked) {
  'use strict';
  const STATUSES = ['Not started', 'In progress', 'Complete', 'Not accessible', 'Skipped'];
  function hash(text) {
    let value = 2166136261;
    for (const character of text) value = Math.imul(value ^ character.codePointAt(0), 16777619);
    return (value >>> 0).toString(36);
  }
  const normalized = text => text.normalize('NFKC').toLowerCase().replace(/^\s*\d+[.)\s]+/, '').trim();
  function plain(text) {
    function read(tokens) {
      return tokens.map(token => token.tokens ? read(token.tokens) : token.type === 'html' ? '' : token.text || token.raw || '').join('');
    }
    return read(marked.Lexer.lexInline(text)).trim();
  }
  function parse(markdown, filename = 'Workbook.md') {
    if (typeof markdown !== 'string' || !markdown.trim()) throw new Error('Choose a Markdown file with some content.');
    if (markdown.length > 500000) throw new Error('Markdown files must contain fewer than 500,000 characters.');
    const tokens = marked.lexer(markdown, {gfm: true});
    const titleToken = tokens.find(token => token.type === 'heading');
    const schema = {title: titleToken ? plain(titleToken.text) : filename.replace(/\.md$/i, ''), metadata: {}, sections: [], fields: [], checks: []};
    const seen = new Map();
    const unique = key => { const count = (seen.get(key) || 0) + 1; seen.set(key, count); return count === 1 ? key : `${key}-${count}`; };
    const sectionId = label => unique(`s-${hash(label)}`);
    let section = {id: 'overview', title: 'Overview', depth: 1, path: 'Overview', blocks: [], items: []};
    schema.sections.push(section);
    const headings = [];
    let consumedTitle = false;
    let tableMode = null;
    function prose(raw) {
      const previous = section.blocks.at(-1);
      if (previous?.type === 'prose') previous.markdown += raw;
      else section.blocks.push({type: 'prose', markdown: raw});
    }
    for (const token of tokens) {
      if (token.type === 'heading') {
        if (!consumedTitle && token === titleToken) { consumedTitle = true; continue; }
        const title = plain(token.text);
        while (headings.length && headings.at(-1).depth >= token.depth) headings.pop();
        const path = [...headings.map(item => normalized(item.title)), normalized(title)].join('/');
        section = {id: sectionId(path), title, depth: token.depth, path, blocks: [], items: []};
        headings.push({depth: token.depth, title});
        schema.sections.push(section);
        tableMode = null;
        continue;
      }
      if (token.type === 'html' && /<!--\s*evidence:(form|reference)\s*-->/.test(token.raw)) {
        tableMode = token.raw.includes('evidence:form') ? 'form' : 'reference';
        continue;
      }
      if (token.type === 'paragraph' && section.id === 'overview') {
        for (const line of token.raw.split('\n')) {
          const inline = marked.Lexer.lexInline(line);
          if (inline[0]?.type === 'strong') schema.metadata[plain(inline[0].text).replace(/:$/, '').toLowerCase()] = plain(line.slice(inline[0].raw.length));
        }
      }
      if (token.type === 'table') {
        const headers = token.header.map(cell => plain(cell.text));
        const rows = token.rows.map(row => row.map(cell => plain(cell.text)));
        const keyValue = headers.length === 2 && /answer|response|value|your input/i.test(headers[1]);
        const pivot = headers.length > 1 && /^field$/i.test(headers[0]);
        const editable = tableMode !== 'reference' && (tableMode === 'form' || keyValue || pivot || rows.some(row => row.some(value => !value.trim())));
        tableMode = null;
        if (!editable) { prose(token.raw + '\n'); continue; }
        const id = unique(`${section.id}/t-${hash(headers.join('|'))}`);
        const table = {type: 'table', id, sectionId: section.id, headers, rows, kind: keyValue ? 'keyValue' : pivot ? 'pivot' : 'records', items: []};
        function field(item, row, column, label) {
          const value = rows[row][column] || '';
          const id = unique(`${item.id}/f-${hash(normalized(label))}`);
          const entry = {id, sectionId: section.id, tableId: table.id, itemId: item.id, itemLabel: item.label, label, row, column, default: value};
          item.fields.push(entry);
          schema.fields.push(entry);
        }
        if (pivot) {
          headers.slice(1).forEach((label, index) => {
            const item = {id: unique(`${id}/i-${hash(normalized(label))}`), label, fields: []};
            rows.forEach((row, rowIndex) => field(item, rowIndex, index + 1, row[0] || `Field ${rowIndex + 1}`));
            table.items.push(item);
          });
        } else {
          rows.forEach((row, rowIndex) => {
            const label = keyValue ? row[0] : row.slice(0, 2).filter(Boolean).join(' / ') || `Entry ${rowIndex + 1}`;
            const item = {id: unique(`${id}/i-${hash(normalized(label))}`), label, fields: []};
            if (keyValue) field(item, rowIndex, 1, row[0] || `Answer ${rowIndex + 1}`);
            else headers.forEach((header, column) => field(item, rowIndex, column, header));
            table.items.push(item);
          });
        }
        section.blocks.push(table);
        section.items.push(...table.items);
        continue;
      }
      if (token.type === 'list' && token.items.some(item => item.task)) {
        const items = token.items.map(item => {
          if (!item.task) return {text: item.text, id: null};
          const label = plain(item.text);
          const entry = {id: unique(`${section.id}/c-${hash(normalized(label))}`), label, default: Boolean(item.checked), sectionId: section.id};
          schema.checks.push(entry);
          return {...entry, text: item.text};
        });
        section.blocks.push({type: 'checklist', items});
        continue;
      }
      if (token.type === 'paragraph' && /^\[write here\]$/i.test(token.text.trim())) {
        const item = {id: unique(`${section.id}/notes`), label: 'Observations', fields: []};
        const entry = {id: `${item.id}/answer`, sectionId: section.id, itemId: item.id, itemLabel: item.label, label: 'Additional observations', default: ''};
        item.fields.push(entry);
        schema.fields.push(entry);
        section.items.push(item);
        section.blocks.push({type: 'notes', item});
        continue;
      }
      prose(token.raw || '');
    }
    return schema;
  }
  const value = (project, field) => Object.hasOwn(project.values, field.id) ? project.values[field.id] : field.default;
  const checked = (project, item) => Object.hasOwn(project.checks, item.id) ? project.checks[item.id] : item.default;
  function catalog(schema) {
    return Object.fromEntries([...schema.fields, ...schema.checks].map(field => [field.id, {label: field.label, sectionId: field.sectionId, itemLabel: field.itemLabel || ''}]));
  }
  function create(markdown, filename, id) {
    const schema = parse(markdown, filename);
    return {id, version: 1, filename, markdown, title: schema.metadata.product || schema.title, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), values: {}, checks: {}, statuses: {}, catalog: catalog(schema)};
  }
  function revise(project, markdown, filename) {
    const schema = parse(markdown, filename);
    return {...project, markdown, filename, title: schema.metadata.product || schema.title, catalog: {...project.catalog, ...catalog(schema)}, updatedAt: new Date().toISOString()};
  }
  function unmatched(project, schema) {
    const live = new Set([...schema.fields, ...schema.checks].map(field => field.id));
    return [...Object.entries(project.values), ...Object.entries(project.checks)].filter(([key]) => !live.has(key));
  }
  function filledRows(project, table) {
    const rows = table.rows.map(row => [...row]);
    for (const item of table.items) for (const field of item.fields) rows[field.row][field.column] = value(project, field);
    return rows;
  }
  const cell = text => String(text ?? '').replace(/\|/g, '\\|').replace(/\r?\n/g, '<br>');
  function report(project, schema, images) {
    let text = `# ${schema.title}\n\nExported: ${new Date().toISOString()}\n\n`;
    for (const section of schema.sections) {
      text += `## ${section.title}\n\nStatus: ${project.statuses[section.id] || 'Not started'}\n\n`;
      for (const block of section.blocks) {
        if (block.type === 'prose') text += `${block.markdown}\n\n`;
        if (block.type === 'table') {
          text += '<!-- evidence:form -->\n';
          text += `| ${block.headers.map(cell).join(' | ')} |\n| ${block.headers.map(() => '---').join(' | ')} |\n`;
          for (const row of filledRows(project, block)) text += `| ${row.map(cell).join(' | ')} |\n`;
          text += '\n';
        }
        if (block.type === 'notes') text += `**${block.item.label}**\n\n${value(project, block.item.fields[0])}\n\n`;
        if (block.type === 'checklist') for (const item of block.items) text += item.id ? `- [${checked(project, item) ? 'x' : ' '}] ${item.text}\n` : `- ${item.text}\n`;
      }
      for (const image of images.filter(image => image.sectionId === section.id)) {
        text += `\n### ${image.label} - ${image.contextLabel}\n\n${image.caption || ''}\n\nSource: ${image.source || 'Not recorded'}\n\nFile: images/${image.id}.${image.extension}\n\n`;
      }
    }
    const old = unmatched(project, schema);
    if (old.length) text += '\n## Saved answers needing review\n\n' + old.map(([key, answer]) => `- ${project.catalog[key]?.label || key}: ${String(answer)}`).join('\n');
    return text;
  }
  return {STATUSES, parse, plain, create, revise, value, checked, unmatched, filledRows, report};
});
