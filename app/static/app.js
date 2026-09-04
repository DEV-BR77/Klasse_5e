(() => {
  const live = document.querySelector("#live-status");
  const announce = (text) => { if (live) live.textContent = text; };
  const csrf = () => document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] || "";
  const presentation = document.querySelector("[data-presentation]");
  if (presentation) {
    const slides = [...presentation.querySelectorAll("[data-slide]")];
    const previous = presentation.querySelector("[data-slide-prev]");
    const next = presentation.querySelector("[data-slide-next]");
    const count = presentation.querySelector("[data-slide-count]");
    const progress = presentation.querySelector("[data-slide-progress]");
    const dots = presentation.querySelector("[data-slide-dots]");
    let index = 0;
    const show = (target) => {
      index = Math.max(0, Math.min(slides.length - 1, target));
      slides.forEach((slide, position) => slide.classList.toggle("is-active", position === index));
      [...dots.children].forEach((dot, position) => dot.classList.toggle("is-active", position === index));
      previous.disabled = index === 0;
      next.textContent = index === slides.length - 1 ? "Von vorn ↺" : "Weiter →";
      count.textContent = `${index + 1} / ${slides.length}`;
      progress.value = index + 1;
    };
    slides.forEach((_slide, position) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.setAttribute("aria-label", `Folie ${position + 1}`);
      dot.addEventListener("click", () => show(position));
      dots.append(dot);
    });
    previous.addEventListener("click", () => show(index - 1));
    next.addEventListener("click", () => show(index === slides.length - 1 ? 0 : index + 1));
    presentation.querySelector("[data-demo-cancel]")?.addEventListener("click", () => {
      const result = presentation.querySelector("[data-cancel-result]");
      result.textContent = "🔔 07:45 Mathematik fällt aus · Kalender automatisch aktualisiert";
      result.classList.add("is-notified");
    });
    presentation.querySelector("[data-demo-push]")?.addEventListener("click", () => {
      const result = presentation.querySelector("[data-push-result]");
      result.textContent = "🔔 Du wurdest im Chat „Klassenfrühstück“ erwähnt.";
      result.classList.add("is-notified");
    });
    show(0);
  }
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
  document.querySelectorAll("[data-gallery-upload]").forEach((form) => form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("button[type='submit']");
    if (button) { button.disabled = true; button.textContent = "Wird verarbeitet …"; }
    const response = await fetch(form.action, {method: "POST", body: new FormData(form), credentials: "same-origin"});
    if (response.ok) { window.location.reload(); return; }
    if (button) { button.disabled = false; button.textContent = "Sicher hochladen"; }
    const data = await response.json().catch(() => ({}));
    window.alert(data.error === "gallery_quota_exceeded" ? "Der Speicherplatz dieser Galerie ist ausgeschöpft." : "Das Bild konnte nicht verarbeitet werden. Bitte prüfe Dateityp und Größe.");
  }));

  const readJsonScript = (id, fallback) => {
    try { return JSON.parse(document.getElementById(id)?.textContent || JSON.stringify(fallback)); } catch (_) { return fallback; }
  };
  const initLeafletMap = (container) => {
    const bounds = readJsonScript(container.dataset.boundsId, {south:52.329, west:10.623, north:52.509, east:10.913});
    const points = readJsonScript(container.dataset.pointsId, []);
    const loading = container.querySelector(".map-loading");
    loading?.remove();
    container.querySelector("canvas")?.remove();
    const leafletMap = window.L.map(container, {zoomControl:false, scrollWheelZoom:true});
    const southWest = [Number(bounds.south), Number(bounds.west)];
    const northEast = [Number(bounds.north), Number(bounds.east)];
    const validPoints = points.filter((point) => Number.isFinite(Number(point.latitude)) && Number.isFinite(Number(point.longitude)));
    const schoolPoint = validPoints.find((point) => point.kind === "school") || validPoints[0];
    if (validPoints.length > 1) {
      leafletMap.fitBounds(window.L.latLngBounds(validPoints.map((point) => [Number(point.latitude), Number(point.longitude)])), {padding:[42, 42], maxZoom:15});
    } else if (schoolPoint) {
      leafletMap.setView([Number(schoolPoint.latitude), Number(schoolPoint.longitude)], 13);
    } else {
      leafletMap.fitBounds([southWest, northEast], {padding:[18, 18]});
    }
    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap-Mitwirkende</a>',
    }).addTo(leafletMap);
    window.L.control.zoom({position:"topright"}).addTo(leafletMap);
    validPoints.forEach((point) => {
      const latitude = Number(point.latitude);
      const longitude = Number(point.longitude);
      const school = point.kind === "school";
      const marker = window.L.circleMarker([latitude, longitude], {
        radius: school ? 9 : 8,
        color: "#fff",
        weight: 3,
        fillColor: school ? "#ec6f5f" : "#6256c7",
        fillOpacity: 1,
      }).addTo(leafletMap);
      if (point.label) marker.bindTooltip(point.label, {permanent: school, direction:"top", offset:[0, -8]});
      if (Number(point.radiusMeters) > 0) {
        window.L.circle([latitude, longitude], {radius:Number(point.radiusMeters), color:"#6256c7", weight:2, fillColor:"#6256c7", fillOpacity:.12}).addTo(leafletMap);
      }
    });
    if (container.dataset.connectPoints === "true" && validPoints.length > 1) {
      window.L.polyline(validPoints.map((point) => [Number(point.latitude), Number(point.longitude)]), {color:"#6256c7", weight:5, opacity:.85, dashArray:"10 8", lineCap:"round", lineJoin:"round"}).addTo(leafletMap);
    }
    if (container.dataset.selectLat && container.dataset.selectLon) {
      let selectedMarker;
      leafletMap.on("click", (event) => {
        const latitude = event.latlng.lat;
        const longitude = event.latlng.lng;
        document.getElementById(container.dataset.selectLat).value = latitude.toFixed(6);
        document.getElementById(container.dataset.selectLon).value = longitude.toFixed(6);
        selectedMarker?.remove();
        selectedMarker = window.L.circleMarker([latitude, longitude], {radius:8, color:"#fff", weight:3, fillColor:"#6256c7", fillOpacity:1}).addTo(leafletMap);
        window.L.circle([latitude, longitude], {radius:Number(container.dataset.selectionRadius || 0), color:"#6256c7", weight:2, fillColor:"#6256c7", fillOpacity:.12}).addTo(leafletMap);
        const output = container.parentElement?.querySelector(".map-selection-status");
        if (output) output.textContent = "Position markiert. Du kannst sie durch erneutes Tippen verschieben.";
      });
    }
    window.setTimeout(() => leafletMap.invalidateSize(), 0);
  };
  document.querySelectorAll("[data-local-map]").forEach(async (map) => {
    if (window.L) { initLeafletMap(map); return; }
    const canvas = map.querySelector("canvas");
    const loading = map.querySelector(".map-loading");
    if (!canvas) return;
    const bounds = readJsonScript(map.dataset.boundsId, {south:52.329, west:10.623, north:52.509, east:10.913});
    const viewBounds = {...bounds};
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
      x: (longitude - viewBounds.west) / (viewBounds.east - viewBounds.west) * width,
      y: (viewBounds.north - latitude) / (viewBounds.north - viewBounds.south) * height,
    });
    const zoom = (factor) => {
      const centerLat = (viewBounds.north + viewBounds.south) / 2;
      const centerLon = (viewBounds.east + viewBounds.west) / 2;
      const halfLat = (viewBounds.north - viewBounds.south) * factor / 2;
      const halfLon = (viewBounds.east - viewBounds.west) * factor / 2;
      const minimum = .006;
      if (halfLat * 2 < minimum || halfLat * 2 > bounds.north - bounds.south) return;
      Object.assign(viewBounds, {south:centerLat-halfLat, north:centerLat+halfLat, west:centerLon-halfLon, east:centerLon+halfLon});
      draw();
    };
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
      route.filter((point) => Number(point.radiusMeters) > 0).forEach((point) => {
        const p = project(Number(point.longitude), Number(point.latitude), width, height);
        const longitudeDegrees = Number(point.radiusMeters) / (111320 * Math.cos(Number(point.latitude) * Math.PI / 180));
        const edge = project(Number(point.longitude) + longitudeDegrees, Number(point.latitude), width, height);
        context.beginPath(); context.arc(p.x, p.y, Math.max(12, Math.abs(edge.x - p.x)), 0, Math.PI * 2);
        context.fillStyle = "rgb(98 86 199 / 14%)"; context.fill(); context.strokeStyle = "rgb(98 86 199 / 65%)"; context.lineWidth = 2; context.stroke();
      });
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
    const controls = document.createElement("div"); controls.className = "map-controls";
    controls.innerHTML = '<button type="button" aria-label="Karte vergrößern">+</button><button type="button" aria-label="Karte verkleinern">−</button><button type="button" aria-label="Gesamte Karte zeigen">⌂</button>';
    map.appendChild(controls);
    controls.children[0].addEventListener("click", () => zoom(.58));
    controls.children[1].addEventListener("click", () => zoom(1.72));
    controls.children[2].addEventListener("click", () => { Object.assign(viewBounds, bounds); draw(); });
    map.addEventListener("wheel", (event) => { event.preventDefault(); zoom(event.deltaY < 0 ? .78 : 1.28); }, {passive:false});
    if (map.dataset.selectLat && map.dataset.selectLon) {
      map.classList.add("is-picker");
      map.addEventListener("click", (event) => {
        const rectangle = canvas.getBoundingClientRect();
        const longitude = viewBounds.west + ((event.clientX - rectangle.left) / rectangle.width) * (viewBounds.east - viewBounds.west);
        const latitude = viewBounds.north - ((event.clientY - rectangle.top) / rectangle.height) * (viewBounds.north - viewBounds.south);
        document.getElementById(map.dataset.selectLat).value = latitude.toFixed(6);
        document.getElementById(map.dataset.selectLon).value = longitude.toFixed(6);
        selected.splice(0, selected.length, {latitude, longitude, label:"Ausgewählt", kind:"start", radiusMeters:Number(map.dataset.selectionRadius || 0)});
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

  document.querySelectorAll("[data-chat-composer]").forEach((composer) => {
    const textarea = composer.querySelector("textarea");
    const picker = composer.querySelector("[data-emoji-picker]");
    const fileInput = composer.querySelector("[data-chat-file]");
    const status = composer.querySelector("[data-composer-status]");
    const mentionNames = readJsonScript("chat-mention-names", []);
    const mentionPicker = document.createElement("div"); mentionPicker.className = "mention-picker"; mentionPicker.hidden = true; composer.appendChild(mentionPicker);
    const insertMention = (name) => {
      const cursor = textarea.selectionStart ?? textarea.value.length;
      const before = textarea.value.slice(0, cursor).replace(/@[\p{L}\p{N} ._-]*$/u, `@${name} `);
      textarea.value = before + textarea.value.slice(cursor); textarea.focus(); mentionPicker.hidden = true;
    };
    textarea.addEventListener("input", () => {
      const cursor = textarea.selectionStart ?? textarea.value.length;
      const match = textarea.value.slice(0, cursor).match(/@([\p{L}\p{N} ._-]*)$/u);
      if (!match) { mentionPicker.hidden = true; return; }
      const query = match[1].trim().toLocaleLowerCase("de");
      const matches = mentionNames.filter((name) => name.toLocaleLowerCase("de").includes(query)).slice(0, 6);
      mentionPicker.replaceChildren(...matches.map((name) => { const button=document.createElement("button"); button.type="button"; button.textContent=`@${name}`; button.addEventListener("click",()=>insertMention(name)); return button; }));
      mentionPicker.hidden = !matches.length;
    });
    composer.querySelector("[data-emoji-toggle]")?.addEventListener("click", () => { picker.hidden = !picker.hidden; });
    picker?.querySelectorAll("[data-emoji]").forEach((button) => button.addEventListener("click", () => {
      const start = textarea.selectionStart ?? textarea.value.length;
      textarea.value = `${textarea.value.slice(0,start)}${button.dataset.emoji}${textarea.value.slice(start)}`;
      textarea.focus(); picker.hidden = true;
    }));
    fileInput?.addEventListener("change", () => { if (fileInput.files[0]) status.textContent = `Anhang: ${fileInput.files[0].name}`; });
    const recordButton = composer.querySelector("[data-voice-record]");
    let recorder;
    let chunks = [];
    recordButton?.addEventListener("click", async () => {
      if (recorder?.state === "recording") { recorder.stop(); return; }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({audio:true});
        recorder = new MediaRecorder(stream); chunks = [];
        recorder.addEventListener("dataavailable", (event) => { if (event.data.size) chunks.push(event.data); });
        recorder.addEventListener("stop", () => {
          const type = recorder.mimeType || "audio/webm";
          const file = new File(chunks, `sprachnachricht-${Date.now()}.webm`, {type});
          const transfer = new DataTransfer(); transfer.items.add(file); fileInput.files = transfer.files;
          stream.getTracks().forEach((track) => track.stop());
          recordButton.classList.remove("is-recording"); status.textContent = "Sprachnachricht bereit zum Senden.";
        });
        recorder.start(); recordButton.classList.add("is-recording"); status.textContent = "Aufnahme läuft – zum Beenden erneut tippen.";
      } catch (_) { status.textContent = "Mikrofonzugriff wurde nicht erteilt oder wird nicht unterstützt."; }
    });
  });

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
