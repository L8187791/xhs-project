(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(3000);
  const tabs = [...document.querySelectorAll('a, div, span, button')]
    .filter(e => e.textContent.trim() === '用户');
  let clicked = 0;
  if (tabs.length) {
    tabs.forEach(t => t.click());
    clicked = tabs.length;
    await sleep(5000);
  }
  const t = document.body.innerText.replace(/\s+/g, ' ');
  return JSON.stringify({ clicked: clicked, text: t.slice(0, 2500) });
})()
