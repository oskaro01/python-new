() => {
    const scope = document.querySelector('main') || document;
    const selector = '[data-message-author-role], :is(h1,h2,h3,h4,h5,h6)[data-conversation-role]';
    const candidates = [...scope.querySelectorAll(selector)].filter(element => {
        const ancestor = element.parentElement.closest('[data-message-author-role]');
        return !ancestor;
    });
    if (!candidates.length) return {layout: 'original', message_count: 0};

    const excluded = 'script, style, link, button, input, textarea, select, form, nav, iframe, '
        + '[role="toolbar"], .turn-action-controls, [data-markdown-copy="exclude"], '
        + ':is(h1,h2,h3,h4,h5,h6)[data-conversation-role]';

    function copyContent(node) {
        if (node.nodeType === Node.TEXT_NODE) return node.cloneNode();
        if (node.nodeType !== Node.ELEMENT_NODE || node.matches(excluded)) return null;
        // Native MathML preserves saved formulae without the app's positioned CSS.
        if (node.matches('.katex') && node.querySelector('math')) {
            return node.querySelector('math').cloneNode(true);
        }
        const style = getComputedStyle(node);
        if (node.hidden || node.classList.contains('sr-only')
            || style.display === 'none' || style.visibility === 'hidden') return null;
        const copy = node.cloneNode(false);
        for (const attribute of [...copy.attributes]) {
            if (['class', 'style'].includes(attribute.name)
                || attribute.name.startsWith('data-') || attribute.name.startsWith('on')) {
                copy.removeAttribute(attribute.name);
            }
        }
        if (['pre', 'pre-wrap', 'pre-line', 'break-spaces'].includes(style.whiteSpace)) {
            copy.style.whiteSpace = 'pre-wrap';
        }
        if (node.tagName === 'IMG') {
            copy.src = node.currentSrc || node.src;
            copy.removeAttribute('srcset');
            copy.loading = 'eager';
        }
        if (node.tagName === 'A') copy.href = node.href;
        if (node.tagName === 'DETAILS') copy.open = true;
        for (const child of node.childNodes) {
            const cleaned = copyContent(child);
            if (cleaned) copy.appendChild(cleaned);
        }
        return copy;
    }

    const transcript = document.createElement('main');
    transcript.id = 'pdf-chat-transcript';
    const title = document.createElement('h1');
    title.textContent = document.title || 'Chat conversation';
    transcript.appendChild(title);
    let messageCount = 0;
    for (const candidate of candidates) {
        const role = candidate.getAttribute('data-message-author-role')
            || candidate.getAttribute('data-conversation-role');
        const source = candidate.hasAttribute('data-message-author-role') ? candidate : candidate.parentElement;
        const content = copyContent(source);
        if (!content || (!content.textContent.trim() && !content.querySelector('img,svg,math'))) continue;
        const message = document.createElement('article');
        message.className = 'chat-message';
        message.dataset.pdfRole = role;
        const label = document.createElement('div');
        label.className = 'message-role';
        label.textContent = {user: 'You', assistant: 'ChatGPT', system: 'System', tool: 'Tool'}[role] || role;
        const body = document.createElement('div');
        body.className = 'message-content';
        body.appendChild(content);
        message.append(label, body);
        transcript.appendChild(message);
        messageCount += 1;
    }
    if (!messageCount) return {layout: 'original', message_count: 0};

    // Saved app print rules and virtualized/fixed-height wrappers cannot govern a transcript.
    for (const sheet of [...document.styleSheets]) sheet.disabled = true;
    document.querySelectorAll('style, link[rel="stylesheet"]').forEach(element => element.remove());
    for (const element of [document.documentElement, document.body]) {
        element.removeAttribute('class');
        element.removeAttribute('style');
    }
    document.body.replaceChildren(transcript);
    const printStyle = document.createElement('style');
    printStyle.textContent = `
        @page { size: A4; margin: 16mm; }
        * { box-sizing: border-box; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
        html, body { display: block; width: auto; height: auto; min-height: 0; max-height: none;
            overflow: visible; margin: 0; padding: 0; color: #20252b; background: #fff; }
        body { font: 11pt/1.55 "Segoe UI", Arial, "Nirmala UI", sans-serif; }
        #pdf-chat-transcript { display: block; width: 100%; }
        #pdf-chat-transcript > h1 { font-size: 20pt; line-height: 1.25; margin: 0 0 20pt; }
        .chat-message { display: block; position: static; height: auto; overflow: visible;
            break-inside: auto; margin: 0 0 18pt; padding: 0 0 0 12pt; border-left: 2pt solid #e1e6ec; }
        .chat-message[data-pdf-role="user"] { border-color: #6887b3; background: #f0f5fc; padding: 9pt 12pt; }
        .message-role { font-size: 10pt; font-weight: 700; color: #3d5c86; margin-bottom: 5pt; break-after: avoid; }
        .message-content, .message-content div { height: auto; min-height: 0; max-height: none;
            overflow: visible; position: static; transform: none; overflow-wrap: anywhere; }
        .message-content p { margin: 0 0 8pt; orphans: 3; widows: 3; }
        .message-content h1 { font-size: 17pt; }
        .message-content h2 { font-size: 15pt; }
        .message-content h3 { font-size: 13pt; }
        .message-content h4, .message-content h5, .message-content h6 { font-size: 11pt; }
        .message-content h1, .message-content h2, .message-content h3, .message-content h4,
        .message-content h5, .message-content h6 { line-height: 1.3; margin: 14pt 0 6pt; break-after: avoid; }
        .message-content pre { white-space: pre-wrap; overflow-wrap: anywhere; margin: 8pt 0;
            padding: 8pt; background: #f4f5f7; border: 1px solid #dce1e6; }
        .message-content code { font: 9.5pt/1.5 Consolas, "Courier New", monospace; }
        .message-content blockquote { margin: 8pt 0; padding-left: 12pt; border-left: 2pt solid #b8c2ce; }
        .message-content ul, .message-content ol { padding-left: 22pt; margin: 6pt 0 10pt; }
        .message-content li { margin: 3pt 0; }
        .message-content table { border-collapse: collapse; width: 100%; table-layout: fixed; margin: 10pt 0; }
        .message-content th, .message-content td { border: 1px solid #cbd3dc; padding: 5pt; vertical-align: top; }
        .message-content thead { display: table-header-group; }
        .message-content tr { break-inside: avoid; }
        .message-content img, .message-content svg { max-width: 100%; height: auto; max-height: 80vh; break-inside: avoid; }
        .message-content a { color: #255889; text-decoration: underline; }
        .message-content hr { border: 0; border-top: 1px solid #dce1e6; margin: 12pt 0; }
    `;
    document.head.appendChild(printStyle);
    return {layout: 'chat', message_count: messageCount};
}
