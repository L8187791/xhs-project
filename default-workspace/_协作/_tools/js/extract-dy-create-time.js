(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(5000);
  // SSR data may contain create_time in multiple forms
  const html = document.documentElement.innerHTML;
  const unix = [...html.matchAll(/"create_time":\s*(\d{10})/g)]
    .map(m => parseInt(m[1]))
    .filter((v, i, a) => a.indexOf(v) === i)
    .sort((a, b) => b - a);
  const iso = unix.map(t => new Date(t * 1000).toISOString().slice(0, 10));
  // fallback: text dates like 2025-01-15
  const textDates = [...html.matchAll(/(20\d{2})[-\/](\d{1,2})[-\/](\d{1,2})/g)]
    .map(m => `${m[1]}-${m[2].padStart(2,'0')}-${m[3].padStart(2,'0')}`);
  return JSON.stringify({
    url: location.href,
    createTimeCount: unix.length,
    latestUnix: unix[0] || null,
    latestIso: iso[0] || null,
    firstFew: iso.slice(0, 8),
    textDates: [...new Set(textDates)].slice(0, 10)
  });
})()
