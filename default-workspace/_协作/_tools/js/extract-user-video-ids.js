(() => {
  const list = document.querySelector('[data-e2e="user-post-list"]');
  if (!list) return JSON.stringify({ count: 0, ids: [] });
  const ids = [...new Set(
    [...list.innerHTML.matchAll(/\/video\/(\d{18,})/g)].map(m => m[1])
  )].slice(0, 20);
  return JSON.stringify({ count: ids.length, ids: ids });
})()
