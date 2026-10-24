// Shared footer for all pages.
// Include with: <script src="/_footer.js"></script> before </body>.
(function () {
  const css = `
    .site-footer{margin-top:40px;padding:18px 22px;border-top:0.5px solid var(--iq-border,#2a2f3d);color:var(--iq-muted,#8b90a0);font-size:12px;display:flex;justify-content:center;gap:18px;flex-wrap:wrap}
    .site-footer a{color:var(--iq-muted,#8b90a0);text-decoration:none}
    .site-footer a:hover{color:var(--iq-accent,#4a7efa)}
    .site-footer .sep{opacity:.5}
  `;
  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  const footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.innerHTML = `
    <a href="/">Intake</a>
    <span class="sep">·</span>
    <a href="/dashboard.html">Dashboard</a>
    <span class="sep">·</span>
    <a href="/privacy.html">Privacy Policy</a>
    <span class="sep">·</span>
    <span>&copy; ${new Date().getFullYear()} Claims Intake</span>
  `;
  document.body.appendChild(footer);
})();
