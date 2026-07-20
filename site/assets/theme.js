(() => {
  const KEY = 'genai-ron-appearance';
  const TEXT_SIZE_KEY = 'genai-ron-article-text-size';
  const THEMES = ['paper', 'reading', 'archive'];
  const LABELS = { paper: 'Paper', reading: 'Reading', archive: 'Archive' };
  const TEXT_SIZES = ['small', 'normal', 'large', 'x-large'];
  const TEXT_LABELS = {
    small: '小',
    normal: '標準',
    large: '大',
    'x-large': '特大'
  };

  function getStoredTheme() {
    try {
      const value = localStorage.getItem(KEY);
      return THEMES.includes(value) ? value : 'paper';
    } catch (_) {
      return 'paper';
    }
  }

  function setTheme(theme) {
    const next = THEMES.includes(theme) ? theme : 'paper';
    document.documentElement.dataset.appearance = next;
    try { localStorage.setItem(KEY, next); } catch (_) {}
    document.querySelectorAll('[data-appearance-choice]').forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.appearanceChoice === next));
    });
  }

  function getStoredTextSize() {
    try {
      const value = localStorage.getItem(TEXT_SIZE_KEY);
      return TEXT_SIZES.includes(value) ? value : 'normal';
    } catch (_) {
      return 'normal';
    }
  }

  function setTextSize(size, persist = true) {
    const next = TEXT_SIZES.includes(size) ? size : 'normal';
    document.documentElement.dataset.articleTextSize = next;
    if (persist) {
      try { localStorage.setItem(TEXT_SIZE_KEY, next); } catch (_) {}
    }
    document.querySelectorAll('[data-article-text-size-choice]').forEach((button) => {
      const active = button.dataset.articleTextSizeChoice === next;
      button.setAttribute('aria-pressed', String(active));
      if (active) {
        button.setAttribute('aria-current', 'true');
      } else {
        button.removeAttribute('aria-current');
      }
    });
  }

  function shouldMountTextSizeControl() {
    if (!document.body || !document.body.classList.contains('series-page')) {
      return false;
    }
    if (!document.querySelector('.series-main > article.note-box')) {
      return false;
    }
    const path = window.location.pathname;
    return path.includes('/series/genai-shikumi/') || path.includes('/series/genai-shikumi-technical/');
  }

  function mountTextSizeControl() {
    setTextSize(getStoredTextSize(), false);
    if (!shouldMountTextSizeControl() || document.querySelector('.article-text-size-control')) {
      return;
    }

    const seriesMain = document.querySelector('.series-main');
    const article = document.querySelector('.series-main > article.note-box');
    if (!seriesMain || !article) {
      return;
    }

    const control = document.createElement('section');
    control.className = 'article-text-size-control';
    control.setAttribute('aria-label', '記事本文の文字サイズ');

    const label = document.createElement('span');
    label.className = 'article-text-size-label';
    label.textContent = '文字サイズ';
    control.appendChild(label);

    const group = document.createElement('div');
    group.className = 'article-text-size-options';
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', '記事本文の文字サイズを選択');

    TEXT_SIZES.forEach((size) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'article-text-size-button';
      button.textContent = TEXT_LABELS[size];
      button.dataset.articleTextSizeChoice = size;
      button.setAttribute('aria-label', `記事本文の文字サイズを${TEXT_LABELS[size]}にする`);
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => setTextSize(size));
      group.appendChild(button);
    });

    control.appendChild(group);
    seriesMain.insertBefore(control, article);
    setTextSize(getStoredTextSize(), false);
  }

  function mountSwitcher() {
    if (document.querySelector('.appearance-switcher')) {
      setTheme(getStoredTheme());
      return;
    }

    const switcher = document.createElement('div');
    switcher.className = 'appearance-switcher';
    switcher.setAttribute('role', 'group');
    switcher.setAttribute('aria-label', 'Appearance');

    THEMES.forEach((theme) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = LABELS[theme];
      button.dataset.appearanceChoice = theme;
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => setTheme(theme));
      switcher.appendChild(button);
    });

    document.body.appendChild(switcher);
    setTheme(getStoredTheme());
  }

  function escapeHtml(value) {
    return value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function highlightJson(source) {
    const escaped = escapeHtml(source);
    return escaped.replace(/(&quot;(?:\\.|[^&])*?&quot;)(\s*:)?|\b(true|false|null)\b|-?\b\d+(?:\.\d+)?\b|([{}\[\],:])/g, (match, stringToken, colon, literal, punct) => {
      if (stringToken) {
        return colon ? `<span class="syntax-key">${stringToken}</span>${colon}` : `<span class="syntax-string">${stringToken}</span>`;
      }
      if (literal) {
        return `<span class="syntax-literal">${literal}</span>`;
      }
      if (punct) {
        return `<span class="syntax-punctuation">${punct}</span>`;
      }
      return `<span class="syntax-number">${match}</span>`;
    });
  }

  function highlightCodeLike(source) {
    let html = escapeHtml(source);
    html = html.replace(/(\/\/.*)$/gm, '<span class="syntax-comment">$1</span>');
    html = html.replace(/(&quot;.*?&quot;|'.*?'|`.*?`)/g, '<span class="syntax-string">$1</span>');
    html = html.replace(/\b(const|let|var|await|async|return|if|else|for|while|function|type|interface|class|new|true|false|null|undefined)\b/g, '<span class="syntax-keyword">$1</span>');
    html = html.replace(/\b(JSON|Promise|Array|Object|String|Number|Boolean)\b/g, '<span class="syntax-built-in">$1</span>');
    return html;
  }

  function enhanceCodeBlocks() {
    document.querySelectorAll('body.series-page-compact pre code').forEach((code) => {
      if (code.dataset.highlighted === 'true') {
        return;
      }
      const className = code.className || '';
      const text = code.textContent || '';
      const looksLikeJson = className.includes('language-json') || /^\s*[{[]/.test(text);
      const looksLikeCode = /language-(tsx|ts|js|javascript|python|css|html)/.test(className) || /\b(const|let|await|function|return|interface|type)\b/.test(text);

      if (looksLikeJson) {
        code.innerHTML = highlightJson(text);
        code.dataset.highlighted = 'true';
      } else if (looksLikeCode) {
        code.innerHTML = highlightCodeLike(text);
        code.dataset.highlighted = 'true';
      }
    });
  }

  function convertMarkdownTables() {
    document.querySelectorAll('body.series-page-compact article.note-box p').forEach((paragraph) => {
      const text = (paragraph.textContent || '').trim();
      const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
      if (lines.length < 3 || !lines.every((line) => line.startsWith('|') && line.endsWith('|'))) {
        return;
      }
      if (!/^\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|$/.test(lines[1])) {
        return;
      }

      const rows = lines.map((line) => line.slice(1, -1).split('|').map((cell) => cell.trim()));
      const table = document.createElement('table');
      table.className = 'content-table repaired-markdown-table';

      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');
      rows[0].forEach((cell) => {
        const th = document.createElement('th');
        th.textContent = cell;
        headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);
      table.appendChild(thead);

      const tbody = document.createElement('tbody');
      rows.slice(2).forEach((row) => {
        const tr = document.createElement('tr');
        row.forEach((cell) => {
          const td = document.createElement('td');
          td.textContent = cell;
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      paragraph.replaceWith(table);
    });
  }

  function injectDeepDiveStyle() {
    if (document.getElementById('deep-dive-runtime-style')) {
      return;
    }
    const style = document.createElement('style');
    style.id = 'deep-dive-runtime-style';
    style.textContent = `
body.series-page-compact,
body.series-page-compact .series-main > article.note-box{
  font-family:"Hiragino Mincho ProN","Yu Mincho",YuMincho,"Noto Serif JP",serif!important;
  letter-spacing:.015em;
}
body.series-page-compact .series-main > article.note-box{
  background:transparent!important;
  box-shadow:none!important;
  border-top:1px solid var(--theme-line, rgba(151,139,119,.36))!important;
  border-left:0!important;
  border-right:0!important;
  border-bottom:0!important;
  border-radius:0!important;
  color:var(--theme-text, #242424)!important;
}
body.series-page-compact .series-main > article.note-box p,
body.series-page-compact .series-main > article.note-box li{
  font-family:"Hiragino Mincho ProN","Yu Mincho",YuMincho,"Noto Serif JP",serif!important;
  color:var(--theme-text, #242424)!important;
}
body.series-page-compact .series-main > article.note-box pre,
body.series-page-compact .series-main > article.note-box pre code{
  font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace!important;
  letter-spacing:0!important;
}
body.series-page-compact .series-main > article.note-box pre{
  background:#f4f1ea!important;
  border:1px solid rgba(151,139,119,.24)!important;
  border-radius:10px!important;
  color:#2b2b2b!important;
}
body.series-page-compact .series-main > article.note-box pre code{
  background:transparent!important;
  color:inherit!important;
}
body.series-page-compact .series-main > article.note-box :not(pre) > code{
  font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace!important;
  background:rgba(214,62,62,.08)!important;
  color:#c43e3e!important;
}
body.series-page-compact .syntax-key{color:#b8336a;font-weight:650;}
body.series-page-compact .syntax-string{color:#4f7d19;}
body.series-page-compact .syntax-number{color:#8f56cc;}
body.series-page-compact .syntax-literal{color:#b35a00;font-weight:650;}
body.series-page-compact .syntax-punctuation{color:#77726a;}
body.series-page-compact .syntax-keyword{color:#8d4bb3;font-weight:650;}
body.series-page-compact .syntax-built-in{color:#28758f;font-weight:650;}
body.series-page-compact .syntax-comment{color:#8a857c;font-style:italic;}
body.series-page-compact .series-main > article.note-box table{
  table-layout:auto;
  word-break:normal;
  overflow-wrap:break-word;
}
body.series-page-compact .series-main > article.note-box blockquote{
  background:#f1e8d8!important;
  border-left:4px solid var(--theme-accent, #245c63)!important;
  border-radius:8px!important;
}
body.series-page-compact .article-link{
  display:block;
  margin-top:42px;
  padding-top:20px;
  border-top:1px solid var(--theme-line, rgba(151,139,119,.36));
  color:var(--theme-muted, #66625a)!important;
}
@media(max-width:640px){
  body.series-page-compact .series-main > article.note-box{padding-left:0!important;padding-right:0!important;}
  body.series-page-compact .series-main > article.note-box pre{font-size:13px!important;}
}
`;
    document.head.appendChild(style);
  }

  function mountDeepDiveEnhancements() {
    if (!document.body || !document.body.classList.contains('series-page-compact')) {
      return;
    }
    injectDeepDiveStyle();
    convertMarkdownTables();
    enhanceCodeBlocks();
  }

  setTheme(getStoredTheme());
  setTextSize(getStoredTextSize(), false);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      mountSwitcher();
      mountTextSizeControl();
      mountDeepDiveEnhancements();
    });
  } else {
    mountSwitcher();
    mountTextSizeControl();
    mountDeepDiveEnhancements();
  }
})();