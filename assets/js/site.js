(() => {
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
  let searchIndex = Array.isArray(window.MITAOJUN_SEARCH_INDEX) ? window.MITAOJUN_SEARCH_INDEX : [];

  if (searchForm && searchInput && searchResults) {
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
        return `<li><a href=\"${item.url}\">${item.title}</a>${meta ? `<p class=\"search-result-meta\">${meta}</p>` : ''}</li>`;
      }).join('');
    };

    const runSearch = () => {
      const keyword = searchInput.value.trim().toLowerCase();
      const results = searchIndex.filter((item) => {
        const blob = `${item.title} ${item.category || ''} ${item.text || ''}`.toLowerCase();
        return blob.includes(keyword);
      });
      render(results, keyword);
    };

    searchForm.addEventListener('submit', (event) => {
      event.preventDefault();
      runSearch();
    });

    searchInput.addEventListener('input', () => {
      runSearch();
    });

    // Prefer full-site index; many pages still contain a tiny inline fallback list.
    if (searchIndex.length < 150) {
      loadScript('/assets/js/search-index.js')
        .then(() => {
          if (Array.isArray(window.MITAOJUN_SEARCH_INDEX) && window.MITAOJUN_SEARCH_INDEX.length) {
            searchIndex = window.MITAOJUN_SEARCH_INDEX;
            if (searchInput.value.trim()) runSearch();
          }
        })
        .catch(() => {
          // Keep fallback inline index silently.
        });
    }
  }
})();
