(() => {
  const escapeHtml = (str) => String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

  const escapeRegExp = (str) => String(str || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  const highlightText = (text, keyword) => {
    if (!keyword) return escapeHtml(text);
    const safe = escapeRegExp(keyword);
    return escapeHtml(text).replace(new RegExp(safe, 'gi'), '<mark class="search-hit">$&</mark>');
  };

  const buildContextSnippet = (item, keyword) => {
    const source = String(item.fulltext || item.text || '');
    if (!source) return '';
    const lower = source.toLowerCase();
    const needle = keyword.toLowerCase();
    const idx = lower.indexOf(needle);
    if (idx < 0) return source.slice(0, 88);
    const start = Math.max(0, idx - 28);
    const end = Math.min(source.length, idx + keyword.length + 46);
    const left = start > 0 ? '…' : '';
    const right = end < source.length ? '…' : '';
    return `${left}${source.slice(start, end)}${right}`;
  };

  const loadScript = (src) => new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${src}"]`);
    if (existing) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(script);
  });

  const yearNode = document.getElementById('year');
  if (yearNode) {
    yearNode.textContent = String(new Date().getFullYear());
  }

  const kickerCategory = document.querySelector('.post-kicker .kicker-category');
  if (kickerCategory) {
    const text = (kickerCategory.textContent || '').trim();
    if (!text || text === '网络') {
      kickerCategory.remove();
      const sep = document.querySelector('.post-kicker .kicker-sep');
      if (sep) sep.remove();
    }
  }

  if (document.body.classList.contains('page-post')) {
    const actions = document.createElement('nav');
    actions.className = 'post-mobile-actions';
    actions.setAttribute('aria-label', '快捷操作');

    const topAction = document.createElement('a');
    topAction.href = '#top';
    topAction.textContent = '顶部';

    actions.append(topAction);
    document.body.appendChild(actions);
  }

  const searchForm = document.getElementById('sidebar-search-form');
  const searchInput = document.getElementById('sidebar-search-input');
  const searchResults = document.getElementById('sidebar-search-results');
  const isSearchPage = document.body.classList.contains('page-search') || window.location.pathname.endsWith('/search.html') || window.location.pathname === '/search.html';
  let searchIndex = Array.isArray(window.MITAOJUN_SEARCH_INDEX) ? window.MITAOJUN_SEARCH_INDEX : [];

  if (searchForm && searchInput) {
    searchForm.setAttribute('action', '/search.html');
    searchForm.setAttribute('method', 'get');
    searchInput.setAttribute('name', 'q');
  }

  if (searchForm && searchInput && searchResults) {
    let fullIndexPromise = null;

    const needsFullIndex = () => searchIndex.length < 150;
    const ensureFullIndexLoaded = () => {
      if (!needsFullIndex()) return Promise.resolve();
      if (fullIndexPromise) return fullIndexPromise;
      fullIndexPromise = loadScript('/assets/js/search-index.js')
        .then(() => {
          if (Array.isArray(window.MITAOJUN_SEARCH_INDEX) && window.MITAOJUN_SEARCH_INDEX.length) {
            searchIndex = window.MITAOJUN_SEARCH_INDEX;
          }
        })
        .catch(() => {
          // Keep fallback inline index silently.
        });
      return fullIndexPromise;
    };

    const metaText = (item) => {
      const parts = [];
      if (item.category && item.category !== '网络') parts.push(item.category);
      if (item.date) parts.push(item.date);
      return parts.join(' / ');
    };

    const render = (items, keyword) => {
      if (!keyword) {
        searchResults.innerHTML = '';
        return;
      }
      if (!items.length) {
        searchResults.innerHTML = '<li class="search-empty">没有找到相关结果</li>';
        return;
      }
      searchResults.innerHTML = items.slice(0, 12).map((item) => {
        const meta = metaText(item);
        const title = highlightText(item.title, keyword);
        const snippet = highlightText(buildContextSnippet(item, keyword), keyword);
        return `<li><a href=\"${item.url}\">${title}</a>${meta ? `<p class=\"search-result-meta\">${meta}</p>` : ''}${snippet ? `<p class=\"search-result-snippet\">${snippet}</p>` : ''}</li>`;
      }).join('');
    };

    const runSearch = (rawKeyword) => {
      const keyword = String(rawKeyword || '').trim().toLowerCase();
      const results = searchIndex.filter((item) => {
        const blob = `${item.title} ${item.category || ''} ${item.text || ''} ${item.fulltext || ''}`.toLowerCase();
        return blob.includes(keyword);
      });
      render(results, keyword);
    };

    if (isSearchPage) {
      const params = new URLSearchParams(window.location.search);
      const keyword = (params.get('q') || params.get('keyword') || '').trim();
      if (keyword) {
        searchInput.value = keyword;
        searchResults.innerHTML = '<li class="search-empty">正在搜索…</li>';
        ensureFullIndexLoaded().then(() => {
          runSearch(keyword);
        });
      }
    } else {
      searchResults.innerHTML = '';
    }
  }
})();
