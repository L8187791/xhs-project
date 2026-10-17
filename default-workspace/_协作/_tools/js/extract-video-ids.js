(() => {
  const html = document.documentElement.innerHTML;
  const ids = [...new Set(
    [...html.matchAll(/\/video\/(\d{18,})/g)].map(m => m[1])
  )].slice(0, 12);
  return JSON.stringify({ count: ids.length, ids: ids });
})()
