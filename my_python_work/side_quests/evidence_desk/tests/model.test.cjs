const {test} = require('node:test');
const assert = require('node:assert/strict');
const M = require('../model.js');
const source = '# Pack\n\n**Product:** Example\n\n## 1. Inputs\n\n| Required input | Your answer |\n| --- | --- |\n| Price | |\n| Cost | |\n\n## 2. Markets\n\n| Country | Phrase | Result |\n| --- | --- | --- |\n| UAE | hello \\| world | |\n| KSA | هواء | |\n\n## 3. Videos\n\n| Field | Video 1 | Video 2 |\n| --- | --- | --- |\n| Creator | | |\n| URL | | |\n\n## 4. Finish\n\n- [ ] Evidence attached\n- [x] Read brief\n\n[Write here]\n';
test('parses answer, record, pivot and checklist layouts', () => {
  const schema = M.parse(source);
  assert.equal(schema.metadata.product, 'Example');
  assert.equal(schema.sections.length, 5);
  assert.equal(schema.fields.length, 13);
  assert.equal(schema.sections[2].blocks.find(block => block.type === 'table').rows[0][1], 'hello | world');
  assert.equal(schema.sections[3].items[0].label, 'Video 1');
  assert.equal(schema.checks[1].default, true);
});
test('template revisions preserve answers through section renumbering', () => {
  const project = M.create(source, 'pack.md', 'one');
  const schema = M.parse(source); const field = schema.fields[0];
  project.values[field.id] = 'AED 200';
  const updated = M.revise(project, source.replace('1. Inputs', '11. Inputs').replace('| Cost | |', '| New cost | |'), 'new.md');
  const next = M.parse(updated.markdown);
  assert.equal(next.fields[0].id, field.id);
  assert.equal(M.value(updated, next.fields[0]), 'AED 200');
  assert.equal(M.unmatched(updated, next).length, 0);
  updated.values[schema.fields[1].id] = 'Retained old cost';
  assert.equal(M.unmatched(updated, next)[0][1], 'Retained old cost');
});
test('reference marker prevents editing; form marker allows filled tables', () => {
  const schema = M.parse('# Pack\n\n<!-- evidence:reference -->\n\n| A | B |\n| --- | --- |\n| x | |\n\n<!-- evidence:form -->\n\n| Name | Answer |\n| --- | --- |\n| q | filled |\n');
  assert.equal(schema.fields.length, 1);
  assert.equal(schema.fields[0].default, 'filled');
});
test('duplicate field names have unique identities and report keeps answers', () => {
  const text = '# Pack\n\n| Field | Video 1 |\n| --- | --- |\n| URL | |\n| URL | |\n';
  const schema = M.parse(text); assert.equal(new Set(schema.fields.map(field => field.id)).size, 2);
  const project = M.create(text, 'pack.md', 'id'); project.values[schema.fields[0].id] = '=SUM(1,2)';
  assert.match(M.report(project, schema, []), /=SUM\(1,2\)/);
});
test('empty and oversized Markdown are rejected', () => {
  assert.throws(() => M.parse('')); assert.throws(() => M.parse('x'.repeat(500001)));
});
test('reference tables can be made editable without shifting existing answer IDs', () => {
  const text = '# Pack\n\n| Name | Result |\n| --- | --- |\n| Existing | Ready |\n\n| Name | Result |\n| --- | --- |\n| Next | |\n';
  const schema = M.parse(text);
  const reference = schema.sections[0].blocks.find(block => block.type === 'referenceTable');
  const project = M.customize(M.create(text, 'pack.md', 'one'), {tableModes: {[reference.id]: true}});
  const edited = M.parse(text, 'pack.md', project);
  assert.equal(edited.sections[0].blocks.filter(block => block.type === 'table').length, 2);
  assert.deepEqual(edited.fields.filter(field => !field.tableId.includes('/r-')).map(field => field.id), schema.fields.map(field => field.id));
  assert.equal(project.markdown, text);
});
test('manual answers have stable identity, placement and export after revisions', () => {
  const project = M.create('# Pack\n\n## 1. Questions\n\nWhat did you find?\n', 'pack.md', 'one');
  const base = M.parse(project.markdown);
  const section = base.sections[1];
  let next = M.customize(project, {manualAnswers: [{id: 'm-custom', sectionId: section.id, afterId: section.blocks[0].id, label: 'My findings'}]});
  next.values['m-custom/answer'] = 'Evidence collected';
  let schema = M.parse(next.markdown, next.filename, next);
  assert.equal(schema.sections[1].blocks[1].item.id, 'm-custom');
  assert.match(M.report(next, schema, []), /My findings[\s\S]*Evidence collected/);
  next = M.customize(next, {manualAnswers: [{...next.manualAnswers[0], label: 'Renamed question'}]});
  next = M.revise(next, next.markdown.replace('1. Questions', '10. Questions').replace('What did you find?', 'Changed source paragraph.'), 'updated.md');
  schema = M.parse(next.markdown, next.filename, next);
  assert.equal(schema.sections[1].blocks.at(-1).item.label, 'Renamed question');
  assert.equal(M.value(next, schema.fields[0]), 'Evidence collected');
  assert.equal(M.unmatched(next, schema).length, 0);
  next = M.revise(next, '# Pack\n\n## Different section\n', 'changed.md');
  assert.equal(M.unmatched(next, M.parse(next.markdown, next.filename, next))[0][1], 'Evidence collected');
});
test('customization validation rejects malformed or excessive additions', () => {
  assert.deepEqual(M.customizations({}), {tableModes: {}, manualAnswers: []});
  assert.throws(() => M.customizations({manualAnswers: [{id: 'bad'}]}));
  assert.throws(() => M.customizations({manualAnswers: Array(201).fill({})}));
  assert.throws(() => M.customizations({tableModes: {__unsafe: true}}));
  assert.throws(() => M.customizations({manualAnswers: [{id: 'm-a', sectionId: 'overview', afterId: null, label: '   '}]}));
});
