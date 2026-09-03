(() => {
  const live = document.querySelector("#live-status");
  const announce = (text) => { if (live) live.textContent = text; };
  const csrf = () => document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] || "";
  document.querySelectorAll("[data-auto-submit]").forEach((form) => form.addEventListener("change", () => form.requestSubmit()));
  document.querySelectorAll("[data-list-filter]").forEach((input) => input.addEventListener("input", () => {
    const list = document.getElementById(input.dataset.listFilter);
    const query = input.value.trim().toLocaleLowerCase("de");
    list?.querySelectorAll("[data-filter-text]").forEach((item) => { item.hidden = !item.dataset.filterText.includes(query); });
  }));
  document.querySelectorAll("[data-confirm]").forEach((form) => form.addEventListener("submit", (event) => { if (!window.confirm(form.dataset.confirm)) event.preventDefault(); }));
  document.querySelectorAll("[data-dialog-open]").forEach((button) => button.addEventListener("click", () => document.getElementById(button.dataset.dialogOpen)?.showModal()));
  document.querySelectorAll("[data-dialog-close]").forEach((button) => button.addEventListener("click", () => button.closest("dialog")?.close()));
  document.querySelectorAll("dialog").forEach((dialog) => dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); }));

  const readJsonScript = (id, fallback) => {
    try { return JSON.parse(document.getElementById(id)?.textContent || JSON.stringify(fallback)); } catch (_) { return fallback; }
  };
  document.querySelectorAll("[data-local-map]").forEach(async (map) => {
    const canvas = map.querySelector("canvas");
    const loading = map.querySelector(".map-loading");
    if (!canvas) return;
    const bounds = readJsonScript(map.dataset.boundsId, {south:52.329, west:10.623, north:52.509, east:10.913});
    const points = readJsonScript(map.dataset.pointsId, []);
    let roads = [];
    try {
      const response = await fetch(map.dataset.mapSrc, {cache:"force-cache"});
      if (response.ok) roads = (await response.json()).roads || [];
    } catch (_) { /* the picker remains usable with its local fallback grid */ }
    loading?.remove();
    const selected = [];
    const context = canvas.getContext("2d");
    const project = (longitude, latitude, width, height) => ({
      x: (longitude - bounds.west) / (bounds.east - bounds.west) * width,
      y: (bounds.north - latitude) / (bounds.north - bounds.south) * height,
    });
    const draw = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      const width = Math.max(320, map.clientWidth);
      const height = Math.max(280, map.clientHeight);
      canvas.width = width * ratio; canvas.height = height * ratio;
      canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      context.fillStyle = "#eef2ee"; context.fillRect(0, 0, width, height);
      context.strokeStyle = "#dce4df"; context.lineWidth = 1;
      for (let x=0; x<width; x+=48) { context.beginPath(); context.moveTo(x,0); context.lineTo(x,height); context.stroke(); }
      for (let y=0; y<height; y+=48) { context.beginPath(); context.moveTo(0,y); context.lineTo(width,y); context.stroke(); }
      roads.forEach((road) => {
        context.beginPath();
        road.points.forEach(([longitude, latitude], index) => { const p=project(longitude,latitude,width,height); index ? context.lineTo(p.x,p.y) : context.moveTo(p.x,p.y); });
        const major = ["motorway","trunk","primary","secondary"].includes(road.kind);
        context.strokeStyle = major ? "#c8d0d5" : road.kind === "cycleway" ? "#9fd7b1" : "#dde2e5";
        context.lineWidth = major ? 2.4 : 1.15; context.stroke();
      });
      const route = [...points, ...selected].filter((point) => Number.isFinite(Number(point.latitude)) && Number.isFinite(Number(point.longitude)));
      if (map.dataset.connectPoints === "true" && route.length > 1) {
        context.beginPath(); route.forEach((point,index) => { const p=project(Number(point.longitude),Number(point.latitude),width,height); index ? context.lineTo(p.x,p.y) : context.moveTo(p.x,p.y); });
        context.strokeStyle="#6a54d9"; context.lineWidth=5; context.lineCap="round"; context.lineJoin="round"; context.stroke();
      }
      route.forEach((point,index) => {
        const p=project(Number(point.longitude),Number(point.latitude),width,height);
        const school=point.kind === "school"; context.beginPath(); context.arc(p.x,p.y,school?10:8,0,Math.PI*2); context.fillStyle=school?"#ec6f5f":"#6256c7"; context.fill(); context.lineWidth=3; context.strokeStyle="#fff"; context.stroke();
        if (school || route.length <= 8) { context.font="600 12px system-ui"; context.fillStyle="#263142"; context.fillText(point.label || (school?"Schule":String(index+1)),p.x+12,p.y-10); }
      });
    };
    const observer = new ResizeObserver(draw); observer.observe(map); draw();
    if (map.dataset.selectLat && map.dataset.selectLon) {
      map.classList.add("is-picker");
      map.addEventListener("click", (event) => {
        const rectangle = canvas.getBoundingClientRect();
        const longitude = bounds.west + ((event.clientX - rectangle.left) / rectangle.width) * (bounds.east - bounds.west);
        const latitude = bounds.north - ((event.clientY - rectangle.top) / rectangle.height) * (bounds.north - bounds.south);
        document.getElementById(map.dataset.selectLat).value = latitude.toFixed(6);
        document.getElementById(map.dataset.selectLon).value = longitude.toFixed(6);
        selected.splice(0, selected.length, {latitude, longitude, label:"Ausgewählt", kind:"start"});
        const output = map.parentElement?.querySelector(".map-selection-status");
        if (output) output.textContent = "Position markiert. Du kannst sie durch erneutes Tippen verschieben.";
        draw();
      });
    }
  });

  let installPrompt;
  const installButton = document.querySelector("[data-install-button]");
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    installPrompt = event;
    if (installButton) installButton.hidden = false;
  });
  installButton?.addEventListener("click", async () => {
    if (!installPrompt) return;
    await installPrompt.prompt();
    installPrompt = null;
    installButton.hidden = true;
  });

  const pushStatus = document.querySelector("[data-push-status]");
  document.querySelector("[data-push-enable]")?.addEventListener("click", async () => {
    try {
      if (!("serviceWorker" in navigator) || !("PushManager" in window)) throw new Error("not_supported");
      const config = await fetch("/push/configuration/", {headers: {Accept: "application/json"}}).then((response) => response.json());
      if (!config.supported) throw new Error("not_configured");
      const permission = await Notification.requestPermission();
      if (permission !== "granted") throw new Error("permission_denied");
      const registration = await navigator.serviceWorker.ready;
      const raw = atob(config.public_key.replace(/-/g, "+").replace(/_/g, "/"));
      const key = Uint8Array.from(raw, (character) => character.charCodeAt(0));
      const subscription = await registration.pushManager.subscribe({userVisibleOnly: true, applicationServerKey: key});
      const body = subscription.toJSON();
      body.device_label = document.querySelector("[data-push-device-label]")?.value.trim() || "Browsergerät";
      const response = await fetch("/push/subscriptions/", {method: "POST", headers: {"Content-Type": "application/json", "X-CSRFToken": csrf()}, body: JSON.stringify(body)});
      if (!response.ok) throw new Error("save_failed");
      pushStatus.textContent = "Push wurde auf diesem Gerät aktiviert. Lade die Seite neu, um den Selbsttest zu starten.";
    } catch (error) {
      const labels = {not_supported: "Dieser Browser unterstützt Web Push nicht.", permission_denied: "Die Browserberechtigung wurde nicht erteilt. Du kannst sie in den Website-Einstellungen ändern.", not_configured: "Push ist auf diesem System noch nicht eingerichtet."};
      pushStatus.textContent = labels[error.message] || "Push konnte vorübergehend nicht aktiviert werden.";
    }
  });
  document.querySelectorAll("[data-push-test]").forEach((form) => form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await fetch(form.action, {method: "POST", headers: {"X-CSRFToken": csrf()}, body: new FormData(form)});
    const result = await response.json();
    const labels = {delivered: "An den Push-Dienst übergeben. Ob das Betriebssystem sie angezeigt hat, kann KlassID nicht erkennen.", stale: "Die Geräteverbindung war veraltet und wurde entfernt.", temporary_failure: "Der Push-Dienst ist vorübergehend nicht erreichbar.", permanent_failure: "Der Push-Dienst hat die Nachricht abgelehnt.", rate_limited: "Bitte warte vor einem weiteren Selbsttest."};
    pushStatus.textContent = labels[result.status] || "Der Selbsttest ist derzeit nicht verfügbar.";
  }));
  document.querySelectorAll("[data-push-disable]").forEach((button) => button.addEventListener("click", async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const local = await registration.pushManager.getSubscription();
      if (!local || local.endpoint !== button.dataset.endpoint) throw new Error("not_this_device");
      const response = await fetch("/push/subscriptions/", {method: "DELETE", headers: {"Content-Type": "application/json", "X-CSRFToken": csrf()}, body: JSON.stringify({endpoint: local.endpoint})});
      if (!response.ok) throw new Error("remove_failed");
      await local.unsubscribe();
      pushStatus.textContent = "Push wurde auf diesem Gerät deaktiviert.";
      button.closest(".card")?.remove();
    } catch (error) {
      pushStatus.textContent = error.message === "not_this_device" ? "Dieses Abonnement gehört zu einem anderen deiner Geräte." : "Push konnte auf diesem Gerät nicht deaktiviert werden.";
    }
  }));

  const chat = document.querySelector("[data-chat-poll]");
  if (chat) {
    const status = document.querySelector("[data-chat-status]");
    let latest = chat.dataset.latest || "";
    const poll = async () => {
      try {
        const response = await fetch(`${chat.dataset.chatPoll}${latest ? `?since=${encodeURIComponent(latest)}` : ""}`, {headers: {Accept: "application/json"}});
        if (!response.ok) throw new Error();
        const data = await response.json();
        if (data.messages?.length) window.location.reload();
        status.textContent = `Aktualisiert ${new Date().toLocaleTimeString("de-DE", {hour: "2-digit", minute: "2-digit"})}`;
      } catch (_) {
        status.textContent = "Verbindung unterbrochen";
        announce("Chat-Verbindung unterbrochen. Erneut versuchen.");
      }
    };
    const timer = window.setInterval(poll, 10000);
    window.addEventListener("beforeunload", () => window.clearInterval(timer));
    document.querySelector("[data-chat-retry]")?.addEventListener("click", poll);
  }
})();
