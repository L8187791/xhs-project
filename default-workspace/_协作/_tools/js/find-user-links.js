(() => {
  const html = document.documentElement.innerHTML;
  const ids = [...html.matchAll(/\/user\/([A-Za-z0-9_\-]{15,})/g)].map(x => x[1]);
  return JSON.stringify([...new Set(ids)].slice(0, 12));
})()
