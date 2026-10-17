(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(7000);
  const html = document.documentElement.innerHTML;
  const ids = [...new Set(
    [...html.matchAll(/\/user\/([A-Za-z0-9_\-]{15,})/g)].map(x => x[1])
  )].slice(0, 6);
  const t = document.body.innerText.replace(/\s+/g, ' ');
  const i = t.indexOf('筛选');
  return JSON.stringify({
    url: location.href,
    ids: ids,
    text: (i >= 0 ? t.slice(i) : t).slice(0, 1800)
  });
})()
