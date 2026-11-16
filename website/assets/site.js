// Mobile menu toggle + hover tooltips for charts (any element with data-tip).
(function () {
  var btn = document.querySelector(".menu-btn");
  if (btn) {
    btn.addEventListener("click", function () {
      var side = document.querySelector(".side");
      var open = side.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var tip = document.createElement("div");
  tip.className = "tip";
  tip.setAttribute("role", "status");
  document.body.appendChild(tip);

  function show(e) {
    var t = e.target.closest("[data-tip]");
    if (!t) return;
    tip.textContent = t.getAttribute("data-tip");
    tip.style.opacity = "1";
    move(e);
  }
  function move(e) {
    var x = e.clientX + 14, y = e.clientY + 14;
    var w = tip.offsetWidth, h = tip.offsetHeight;
    if (x + w > window.innerWidth - 8) x = e.clientX - w - 14;
    if (y + h > window.innerHeight - 8) y = e.clientY - h - 14;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }
  function hide(e) {
    if (e.target.closest("[data-tip]")) tip.style.opacity = "0";
  }
  document.addEventListener("pointerover", show);
  document.addEventListener("pointermove", function (e) {
    if (e.target.closest("[data-tip]")) move(e);
  });
  document.addEventListener("pointerout", hide);
})();
