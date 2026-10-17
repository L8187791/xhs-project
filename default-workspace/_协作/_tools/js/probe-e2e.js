(() => {
  const s = new Set();
  document.querySelectorAll('[data-e2e]').forEach(e => s.add(e.getAttribute('data-e2e')));
  const out = {};
  [...s].forEach(k => {
    out[k] = document.querySelectorAll('[data-e2e="' + k + '"]').length;
  });
  return JSON.stringify(out);
})()
