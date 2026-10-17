(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const count = () => document.querySelectorAll('[data-e2e="user-post-list"] li').length;
  const sc = document.querySelector('[data-e2e="scroll-list"]');
  const pl = document.querySelector('[data-e2e="user-post-list"]');
  const trace = [];
  for (let i = 0; i < 22; i++) {
    const targets = [document.scrollingElement, document.documentElement, document.body, sc, pl];
    targets.forEach(n => {
      if (!n) return;
      try { n.scrollTop = n.scrollHeight; } catch (e) { }
    });
    window.scrollTo(0, 999999);
    // synthesize wheel events, which virtualized lists listen for
    [sc, pl].forEach(n => {
      if (!n) return;
      try {
        n.dispatchEvent(new WheelEvent('wheel', { deltaY: 900, bubbles: true, cancelable: true }));
      } catch (e) { }
    });
    await sleep(900);
    trace.push(count());
  }
  await sleep(2500);
  return JSON.stringify({
    tabCount: document.querySelector('[data-e2e="user-tab-count"]') ?
      document.querySelector('[data-e2e="user-tab-count"]').innerText.trim() : null,
    final: count(),
    trace: trace
  });
})()
