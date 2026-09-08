(() => {
  const live = document.querySelector("#live-status");
  const announce = (text) => { if (live) live.textContent = text; };
  const csrf = () => document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] || "";
  const timeoutSeconds = Number(document.body.dataset.idleSessionTimeout || 0);
  if (Number.isFinite(timeoutSeconds) && timeoutSeconds > 0) {
    let timeoutId;
    const endSession = () => {
      fetch("/sessions/idle-timeout/", {
        method: "POST", headers: {"X-CSRFToken": csrf()}, credentials: "same-origin", keepalive: true,
      }).finally(() => window.location.replace("/accounts/login/?timeout=1"));
    };
    const resetIdleTimer = () => {
      window.clearTimeout(timeoutId);
      timeoutId = window.setTimeout(endSession, timeoutSeconds * 1000);
    };
    ["pointerdown", "keydown", "touchstart"].forEach((eventName) => {
      window.addEventListener(eventName, resetIdleTimer, {passive: true});
    });
    resetIdleTimer();
  }
  document.querySelectorAll("[data-dashboard-tabs]").forEach((switcher) => {
    const tabs = [...switcher.querySelectorAll("[data-dashboard-tab]")];
    const panels = [...switcher.querySelectorAll("[data-dashboard-panel]")];
    const select = (key, focus = false) => {
      const selected = tabs.find((tab) => tab.dataset.dashboardTab === key) || tabs[0];
      if (!selected) return;
      tabs.forEach((tab) => {
        const active = tab === selected;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", String(active));
        tab.tabIndex = active ? 0 : -1;
      });
      panels.forEach((panel) => { panel.hidden = panel.dataset.dashboardPanel !== selected.dataset.dashboardTab; });
      if (focus) selected.focus();
    };
    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => select(tab.dataset.dashboardTab));
      tab.addEventListener("keydown", (event) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        let target = index;
        if (event.key === "ArrowLeft") target = (index - 1 + tabs.length) % tabs.length;
        if (event.key === "ArrowRight") target = (index + 1) % tabs.length;
        if (event.key === "Home") target = 0;
        if (event.key === "End") target = tabs.length - 1;
        select(tabs[target].dataset.dashboardTab, true);
      });
    });
    select(tabs.find((tab) => tab.classList.contains("is-active"))?.dataset.dashboardTab || "day");
  });
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
  document.querySelectorAll("[data-replace-history]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const url = new URL(form.action || window.location.href);
      url.search = new URLSearchParams(new FormData(form)).toString();
      window.location.replace(url.href);
    });
  });
  document.querySelectorAll("[data-auto-submit]").forEach((form) => form.addEventListener("change", () => form.requestSubmit()));
  document.querySelectorAll("[data-menu-sort]").forEach((list) => {
    const syncPositions = () => list.querySelectorAll("[data-menu-row]").forEach((row, index) => {
      const input = row.querySelector("input[type='number']");
      if (input) input.value = index + 1;
    });
    list.addEventListener("click", (event) => {
      const button = event.target.closest("[data-menu-up], [data-menu-down]");
      if (!button) return;
      const row = button.closest("[data-menu-row]");
      if (!row) return;
      if (button.hasAttribute("data-menu-up") && row.previousElementSibling) row.parentElement.insertBefore(row, row.previousElementSibling);
      if (button.hasAttribute("data-menu-down") && row.nextElementSibling) row.parentElement.insertBefore(row.nextElementSibling, row);
      syncPositions();
    });
    syncPositions();
  });
  document.querySelectorAll("[data-list-filter]").forEach((input) => input.addEventListener("input", () => {
    const list = document.getElementById(input.dataset.listFilter);
    const query = input.value.trim().toLocaleLowerCase("de");
    list?.querySelectorAll("[data-filter-text]").forEach((item) => { item.hidden = !item.dataset.filterText.includes(query); });
  }));
  document.querySelectorAll("[data-confirm]").forEach((form) => form.addEventListener("submit", (event) => { if (!window.confirm(form.dataset.confirm)) event.preventDefault(); }));
  document.querySelectorAll("[data-contact-table]").forEach((directory) => {
    const rows = directory.querySelector("[data-contact-rows]");
    const filter = directory.querySelector("[data-contact-filter]");
    const count = directory.querySelector("[data-contact-count]");
    const allRows = () => Array.from(rows?.querySelectorAll("[data-contact-row]") || []);
    const refreshCount = () => { if (count) count.textContent = allRows().filter((row) => !row.hidden).length; };
    filter?.addEventListener("input", () => {
      const query = filter.value.trim().toLocaleLowerCase("de");
      allRows().forEach((row) => { row.hidden = !`${row.dataset.family} ${row.dataset.children} ${row.dataset.phone} ${row.dataset.email}`.toLocaleLowerCase("de").includes(query); });
      refreshCount();
    });
    directory.querySelectorAll("[data-contact-sort]").forEach((button) => button.addEventListener("click", () => {
      const key = button.dataset.contactSort;
      const ascending = button.dataset.direction !== "asc";
      directory.querySelectorAll("[data-contact-sort]").forEach((item) => { item.dataset.direction = ""; item.removeAttribute("aria-sort"); });
      button.dataset.direction = ascending ? "asc" : "desc";
      button.setAttribute("aria-sort", ascending ? "ascending" : "descending");
      allRows().sort((left, right) => left.dataset[key].localeCompare(right.dataset[key], "de", { sensitivity: "base" }) * (ascending ? 1 : -1)).forEach((row) => rows.append(row));
    }));
  });
  document.querySelectorAll("[data-dialog-open]").forEach((button) => button.addEventListener("click", () => {
    const dialog = document.getElementById(button.dataset.dialogOpen);
    dialog?.showModal();
    window.setTimeout(() => {
      dialog?.querySelectorAll("[data-local-map]").forEach((map) => {
        map._leafletInstance?.invalidateSize();
        map._leafletRestoreView?.();
      });
    }, 80);
  }));
  document.querySelectorAll("[data-dialog-close]").forEach((button) => button.addEventListener("click", () => button.closest("dialog")?.close()));
  document.querySelectorAll("dialog").forEach((dialog) => dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); }));
  document.querySelectorAll("[data-contribution-builder]").forEach((builder) => {
    const rows = builder.querySelector("[data-contribution-rows]");
    const addRow = builder.querySelector("[data-add-contribution-row]");
    addRow?.addEventListener("click", () => {
      if (!rows || rows.children.length >= 30) return;
      const row = document.createElement("div");
      row.className = "contribution-entry-row";
      row.innerHTML = '<label>Eintrag<input name="bring_label" maxlength="160" placeholder="z. B. Bälle"></label><label>Menge<input name="bring_quantity" type="number" min="0.01" step="0.01" value="1"></label><label>Einheit<input name="bring_unit" maxlength="40" value="Stück"></label>';
      rows.append(row);
      row.querySelector("input")?.focus();
    });
  });
  document.querySelectorAll("[data-family-children]").forEach((section) => {
    const rows = section.querySelector("[data-family-child-rows]");
    const template = document.getElementById("family-child-template");
    const add = section.querySelector("[data-add-family-child]");
    const update = () => rows?.querySelectorAll("[data-family-child-row]").forEach((row, position) => {
      row.querySelector("legend")?.replaceChildren(`Kind ${position + 1}`);
      const index = position + 1;
      row.querySelectorAll("[data-family-child-name]").forEach((input) => {
        input.name = `child_${index}_${input.dataset.familyChildName}`;
      });
      row.querySelectorAll("input").forEach((input) => { input.required = true; });
    });
    add?.addEventListener("click", () => {
      if (!rows || !template) return;
      const row = template.content.cloneNode(true);
      rows.append(row);
      update();
      rows.lastElementChild?.querySelector("input")?.focus();
    });
    rows?.addEventListener("click", (event) => {
      const remove = event.target.closest("[data-remove-family-child]");
      if (!remove) return;
      remove.closest("[data-family-child-row]")?.remove();
      update();
    });
    update();
  });
  document.addEventListener("click", (event) => {
    document.querySelectorAll("details[open]").forEach((details) => {
      if (!details.contains(event.target)) details.removeAttribute("open");
    });
  });
  document.querySelectorAll("details").forEach((details) => details.addEventListener("toggle", () => {
    if (!details.open) return;
    window.setTimeout(() => {
      details.querySelectorAll("[data-local-map]").forEach((map) => {
        map._leafletInstance?.invalidateSize();
        map._leafletRestoreView?.();
      });
    }, 80);
  }));

  const applyHomeworkState = (homeworkId, completed) => {
    document.querySelectorAll(`[data-homework-id="${homeworkId}"]`).forEach((toggle) => {
      toggle.checked = completed;
    });
    document.querySelectorAll(`[data-homework-state-label="${homeworkId}"]`).forEach((label) => {
      label.textContent = completed ? "Erledigt" : "Offen";
    });
    document.querySelector(`[data-homework-row="${homeworkId}"]`)?.classList.toggle("is-completed", completed);
  };
  const saveHomeworkState = async (toggle, completed) => {
    const homeworkId = toggle.dataset.homeworkId;
    const previous = !completed;
    const related = [...document.querySelectorAll(`[data-homework-id="${homeworkId}"]`)];
    applyHomeworkState(homeworkId, completed);
    related.forEach((item) => { item.disabled = true; });
    try {
      const response = await fetch(toggle.dataset.url, {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": csrf(), Accept: "application/json"},
        body: new URLSearchParams({completed: completed ? "yes" : "no"}),
        credentials: "same-origin",
      });
      if (!response.ok) throw new Error("save_failed");
      const data = await response.json();
      applyHomeworkState(homeworkId, Boolean(data.completed));
      announce(data.completed ? "Hausaufgabe als erledigt markiert." : "Hausaufgabe wieder als offen markiert.");
    } catch (_) {
      applyHomeworkState(homeworkId, previous);
      announce("Der Hausaufgabenstatus konnte nicht gespeichert werden.");
    } finally {
      related.forEach((item) => { item.disabled = false; });
    }
  };
  document.querySelectorAll("[data-homework-toggle]").forEach((toggle) => {
    toggle.addEventListener("change", () => saveHomeworkState(toggle, toggle.checked));
  });
  document.querySelectorAll("[data-homework-swipe]").forEach((row) => {
    let start = null;
    row.addEventListener("touchstart", (event) => {
      if (event.target.closest(".homework-completion")) return;
      const touch = event.touches[0];
      start = {x: touch.clientX, y: touch.clientY};
    }, {passive: true});
    row.addEventListener("touchmove", (event) => {
      if (!start) return;
      const touch = event.touches[0];
      const dx = touch.clientX - start.x;
      const dy = touch.clientY - start.y;
      if (dx <= 0 || Math.abs(dx) <= Math.abs(dy)) return;
      event.preventDefault();
      row.classList.add("is-swiping");
      row.style.setProperty("--homework-swipe", `${Math.min(dx, 96)}px`);
    }, {passive: false});
    row.addEventListener("touchend", (event) => {
      if (!start) return;
      const touch = event.changedTouches[0];
      const dx = touch.clientX - start.x;
      const dy = touch.clientY - start.y;
      start = null;
      row.classList.remove("is-swiping");
      row.style.removeProperty("--homework-swipe");
      if (dx < 72 || Math.abs(dx) <= Math.abs(dy)) return;
      event.preventDefault();
      const toggle = row.querySelector("[data-homework-toggle]");
      if (toggle && !toggle.checked && !toggle.disabled) saveHomeworkState(toggle, true);
    });
  });

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

  document.querySelectorAll("[data-profile-form]").forEach((form) => {
    const input = form.querySelector("[data-profile-photo-input]");
    const cropper = form.querySelector("[data-profile-cropper]");
    const viewport = form.querySelector("[data-profile-crop-viewport]");
    const image = form.querySelector("[data-profile-crop-image]");
    const zoomControl = form.querySelector("[data-profile-crop-zoom]");
    const currentPreview = form.querySelector("[data-profile-current-preview] img");
    const photoMode = form.querySelector("[data-profile-photo-mode]");
    if (!input || !cropper || !viewport || !image || !zoomControl) return;

    let objectUrl = "";
    let zoomLevel = 1;
    let offsetX = 0;
    let offsetY = 0;
    let dragStart = null;
    let cropReady = false;

    const clampOffset = () => {
      const width = image.naturalWidth * image._baseScale * zoomLevel;
      const height = image.naturalHeight * image._baseScale * zoomLevel;
      const maxX = Math.max(0, (width - viewport.clientWidth) / 2);
      const maxY = Math.max(0, (height - viewport.clientHeight) / 2);
      offsetX = Math.max(-maxX, Math.min(maxX, offsetX));
      offsetY = Math.max(-maxY, Math.min(maxY, offsetY));
    };
    const renderCrop = () => {
      if (!image._baseScale) return;
      clampOffset();
      const width = image.naturalWidth * image._baseScale * zoomLevel;
      const height = image.naturalHeight * image._baseScale * zoomLevel;
      image.style.width = `${width}px`;
      image.style.height = `${height}px`;
      image.style.left = `${(viewport.clientWidth - width) / 2 + offsetX}px`;
      image.style.top = `${(viewport.clientHeight - height) / 2 + offsetY}px`;
    };
    const prepareCrop = () => {
      if (!image.naturalWidth || !viewport.clientWidth) return;
      image._baseScale = Math.max(
        viewport.clientWidth / image.naturalWidth,
        viewport.clientHeight / image.naturalHeight,
      );
      zoomLevel = 1;
      offsetX = 0;
      offsetY = 0;
      zoomControl.value = "1";
      cropReady = true;
      renderCrop();
    };
    input.addEventListener("change", () => {
      const file = input.files?.[0];
      if (!file) return;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = URL.createObjectURL(file);
      image.src = objectUrl;
      cropper.hidden = false;
      photoMode.disabled = false;
      photoMode.checked = true;
      image.addEventListener("load", prepareCrop, {once:true});
    });
    zoomControl.addEventListener("input", () => {
      zoomLevel = Number(zoomControl.value);
      renderCrop();
    });
    viewport.addEventListener("pointerdown", (event) => {
      if (!cropReady) return;
      dragStart = {x:event.clientX, y:event.clientY, offsetX, offsetY};
      viewport.setPointerCapture(event.pointerId);
    });
    viewport.addEventListener("pointermove", (event) => {
      if (!dragStart) return;
      offsetX = dragStart.offsetX + event.clientX - dragStart.x;
      offsetY = dragStart.offsetY + event.clientY - dragStart.y;
      renderCrop();
    });
    const stopDragging = () => { dragStart = null; };
    viewport.addEventListener("pointerup", stopDragging);
    viewport.addEventListener("pointercancel", stopDragging);

    form.addEventListener("submit", (event) => {
      if (!input.files?.length || !cropReady || form.dataset.profileCropApplied === "yes") return;
      event.preventDefault();
      const width = image.naturalWidth * image._baseScale * zoomLevel;
      const height = image.naturalHeight * image._baseScale * zoomLevel;
      const left = (viewport.clientWidth - width) / 2 + offsetX;
      const top = (viewport.clientHeight - height) / 2 + offsetY;
      const sourceX = Math.max(0, (-left / width) * image.naturalWidth);
      const sourceY = Math.max(0, (-top / height) * image.naturalHeight);
      const sourceWidth = Math.min(image.naturalWidth - sourceX, (viewport.clientWidth / width) * image.naturalWidth);
      const sourceHeight = Math.min(image.naturalHeight - sourceY, (viewport.clientHeight / height) * image.naturalHeight);
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 512;
      canvas.getContext("2d").drawImage(image, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, 512, 512);
      canvas.toBlob((blob) => {
        if (!blob) { form.submit(); return; }
        const transfer = new DataTransfer();
        transfer.items.add(new File([blob], "profilfoto.webp", {type:"image/webp"}));
        input.files = transfer.files;
        form.dataset.profileCropApplied = "yes";
        form.requestSubmit();
      }, "image/webp", .92);
    });
  });

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
    const selectable = Boolean(container.dataset.selectLat && container.dataset.selectLon);
    const fixedPoints = selectable ? validPoints.filter((point) => point.kind === "school") : validPoints;
    const savedSelection = selectable ? validPoints.find((point) => point.kind !== "school") : null;
    const schoolPoint = fixedPoints.find((point) => point.kind === "school") || fixedPoints[0];
    const restoreView = () => {
      if (validPoints.length > 1) {
        leafletMap.fitBounds(window.L.latLngBounds(validPoints.map((point) => [Number(point.latitude), Number(point.longitude)])), {padding:[42, 42], maxZoom:15});
      } else if (schoolPoint) {
        leafletMap.setView([Number(schoolPoint.latitude), Number(schoolPoint.longitude)], 13);
      } else {
        leafletMap.fitBounds([southWest, northEast], {padding:[18, 18]});
      }
    };
    restoreView();
    container._leafletInstance = leafletMap;
    container._leafletRestoreView = restoreView;
    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap-Mitwirkende</a>',
    }).addTo(leafletMap);
    window.L.control.zoom({position:"topright"}).addTo(leafletMap);
    fixedPoints.forEach((point) => {
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
    if (container.dataset.connectPoints === "true" && fixedPoints.length > 1) {
      window.L.polyline(fixedPoints.map((point) => [Number(point.latitude), Number(point.longitude)]), {color:"#6256c7", weight:5, opacity:.85, dashArray:"10 8", lineCap:"round", lineJoin:"round"}).addTo(leafletMap);
    }
    if (selectable) {
      let selectedMarker;
      let selectedCircle;
      const setSelection = (latitude, longitude, writeToForm = true) => {
        if (writeToForm) {
          document.getElementById(container.dataset.selectLat).value = latitude.toFixed(6);
          document.getElementById(container.dataset.selectLon).value = longitude.toFixed(6);
        }
        selectedMarker?.remove();
        selectedCircle?.remove();
        selectedMarker = window.L.circleMarker([latitude, longitude], {radius:8, color:"#fff", weight:3, fillColor:"#6256c7", fillOpacity:1}).addTo(leafletMap);
        selectedCircle = window.L.circle([latitude, longitude], {radius:Number(container.dataset.selectionRadius || 0), color:"#6256c7", weight:2, fillColor:"#6256c7", fillOpacity:.12}).addTo(leafletMap);
      };
      if (savedSelection) setSelection(Number(savedSelection.latitude), Number(savedSelection.longitude), false);
      leafletMap.on("click", (event) => {
        const latitude = event.latlng.lat;
        const longitude = event.latlng.lng;
        setSelection(latitude, longitude);
        const output = container.parentElement?.querySelector(".map-selection-status");
        if (output) output.textContent = "Position markiert. Du kannst sie durch erneutes Tippen verschieben.";
      });
    }
    window.setTimeout(() => { leafletMap.invalidateSize(); restoreView(); }, 0);
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
    const selectable = Boolean(map.dataset.selectLat && map.dataset.selectLon);
    const validPoints = points.filter((point) => Number.isFinite(Number(point.latitude)) && Number.isFinite(Number(point.longitude)));
    const fixedPoints = selectable ? validPoints.filter((point) => point.kind === "school") : validPoints;
    const savedSelection = selectable ? validPoints.find((point) => point.kind !== "school") : null;
    const selected = savedSelection ? [{...savedSelection, kind:"start"}] : [];
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
      const route = [...fixedPoints, ...selected];
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
    if (selectable) {
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
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        status.textContent = "Sprachnachrichten werden von diesem Browser nicht unterstützt. Bitte nutze eine aktuelle Version von Chrome, Edge, Firefox oder Safari.";
        return;
      }
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
      } catch (error) {
        if (error?.name === "NotAllowedError" || error?.name === "SecurityError") {
          status.textContent = "Mikrofon ist blockiert. Öffne links neben der Webadresse die Website-Einstellungen, erlaube das Mikrofon und lade die Seite neu.";
        } else if (error?.name === "NotFoundError") {
          status.textContent = "Es wurde kein Mikrofon gefunden. Bitte prüfe, ob ein Mikrofon angeschlossen und in Windows aktiviert ist.";
        } else if (error?.name === "NotReadableError") {
          status.textContent = "Das Mikrofon wird gerade von einer anderen Anwendung verwendet. Schließe sie und versuche es erneut.";
        } else {
          status.textContent = "Die Aufnahme konnte nicht gestartet werden. Bitte prüfe die Mikrofonfreigabe in den Website-Einstellungen.";
        }
      }
    });
  });

  const chat = document.querySelector("[data-chat-poll]");
  if (chat) {
    const status = document.querySelector("[data-chat-status]");
    let latest = chat.dataset.latest || "";
    const poll = async () => {
      try {
        const response = await fetch(`${chat.dataset.chatPoll}${latest ? `?since=${encodeURIComponent(latest)}` : ""}`, {headers: {Accept: "application/json", "X-KlassID-Background-Poll": "1"}});
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

(() => {
  const dialog = document.querySelector("#avatar-designer");
  if (!dialog) return;
  const data = JSON.parse(document.querySelector("#avatar-designer-data")?.textContent || "{}");
  if (!data.components || !data.backgrounds) return;
  const svgNs = "http://www.w3.org/2000/svg";
  const keys = ["background", "body", "head", "face", "facial-hair", "accessories"];
  const layers = {body: [13, 42, 70, 47], head: [33, 12, 42, 37], face: [47, 24, 25, 20], "facial-hair": [42, 34, 26, 18], accessories: [37, 27, 35, 12]};
  let target;
  let selected = {background: 0, body: 0, head: 0, face: 0, "facial-hair": 0, accessories: 0};
  const assetUrl = (category, filename) => `/static/vendor/avatar-atoms/${category}/${encodeURIComponent(filename)}`;
  const makeSvg = (compact = false) => {
    const svg = document.createElementNS(svgNs, "svg");
    svg.setAttribute("viewBox", "0 0 240 324");
    svg.setAttribute("aria-hidden", "true");
    const background = document.createElementNS(svgNs, "rect");
    background.setAttribute("width", "240"); background.setAttribute("height", "324"); background.setAttribute("rx", "26");
    background.setAttribute("fill", data.backgrounds[selected.background]); svg.append(background);
    Object.entries(layers).forEach(([category, values]) => {
      const filename = data.components[category][selected[category]][0];
      if (!filename) return;
      const image = document.createElementNS(svgNs, "image");
      image.setAttribute("href", assetUrl(category, filename));
      image.setAttribute("x", `${values[0]}%`); image.setAttribute("y", `${values[1]}%`);
      image.setAttribute("width", `${values[2]}%`); image.setAttribute("height", `${values[3]}%`);
      image.setAttribute("preserveAspectRatio", "xMidYMid meet"); svg.append(image);
    });
    if (compact) svg.classList.add("avatar-option-art");
    return svg;
  };
  const draw = () => {
    const preview = dialog.querySelector("[data-avatar-preview]");
    preview.replaceChildren(makeSvg());
    keys.forEach((key) => dialog.querySelectorAll(`[data-avatar-option="${key}"]`).forEach((button) => {
      button.classList.toggle("is-selected", Number(button.dataset.avatarIndex) === selected[key]);
      button.setAttribute("aria-pressed", String(Number(button.dataset.avatarIndex) === selected[key]));
    }));
  };
  const optionButton = (key, index, label) => {
    const button = document.createElement("button"); button.type = "button"; button.className = "avatar-option";
    button.dataset.avatarOption = key; button.dataset.avatarIndex = String(index); button.setAttribute("aria-pressed", "false");
    if (key === "background") { const swatch = document.createElement("span"); swatch.className = "avatar-color-swatch"; swatch.style.background = data.backgrounds[index]; button.append(swatch); }
    else { const art = document.createElement("span"); art.className = "avatar-option-art"; const image = document.createElement("img"); const filename = data.components[key][index][0]; if (filename) { image.src = assetUrl(key, filename); image.alt = ""; } art.append(image); button.append(art); }
    const text = document.createElement("span"); text.textContent = label; button.append(text);
    button.addEventListener("click", () => { selected[key] = index; draw(); }); return button;
  };
  keys.forEach((key) => {
    const holder = dialog.querySelector(`[data-avatar-options="${key}"]`); if (!holder) return;
    const options = key === "background" ? data.backgrounds.map((_, index) => ["", `Farbe ${index + 1}`]) : data.components[key];
    options.forEach((item, index) => holder.append(optionButton(key, index, item[1])));
  });
  dialog.querySelector("[data-avatar-random]").addEventListener("click", () => {
    selected.background = Math.floor(Math.random() * data.backgrounds.length);
    keys.slice(1).forEach((key) => { selected[key] = Math.floor(Math.random() * data.components[key].length); }); draw();
  });
  dialog.querySelector("[data-avatar-apply]").addEventListener("click", () => {
    if (!target) return;
    target.value = `v2:${keys.map((key) => selected[key]).join(":")}`;
    const form = target.closest("form");
    const avatarMode = form.querySelector('[name="profile_image_mode"][value="avatar"]');
    const hiddenMode = form.querySelector('input[type="hidden"][name="profile_image_mode"]');
    if (avatarMode) avatarMode.checked = true;
    if (hiddenMode) hiddenMode.value = "avatar";
    const currentPreview = form.querySelector("[data-profile-current-preview]");
    if (currentPreview) currentPreview.replaceChildren(makeSvg());
    target.dispatchEvent(new Event("change", { bubbles: true }));
  });
  document.querySelectorAll("[data-avatar-open]").forEach((button) => button.addEventListener("click", () => {
    target = button.closest("form").querySelector("[data-avatar-seed]");
    keys.forEach((key) => { selected[key] = 0; });
    const values = target.value.split(":");
    if (values[0] === "v2" && values.length === 7 && values.slice(1).every((value) => /^\d+$/.test(value))) keys.forEach((key, index) => {
      const value = Number(values[index + 1]);
      const limit = key === "background" ? data.backgrounds.length : data.components[key].length;
      selected[key] = value >= 0 && value < limit ? value : 0;
    });
    draw(); dialog.showModal();
  }));
})();
(() => {
  document.querySelectorAll('[data-profile-photo-input]').forEach((input) => input.addEventListener('change', () => {
    const file = input.files?.[0]; if (!file) return;
    const form = input.closest('form'); const preview = form?.querySelector('[data-profile-current-preview]');
    if (!preview) return;
    const image = document.createElement('img'); image.src = URL.createObjectURL(file); image.alt = 'Vorschau des Profilfotos';
    preview.replaceChildren(image); form.querySelector('[data-profile-image-mode]')?.setAttribute('value', 'photo');
  }));
  document.querySelectorAll('[data-toggle-column]').forEach((button) => button.addEventListener('click', () => {
    const inputs = [...button.closest('form').querySelectorAll(`[data-notification-channel="${button.dataset.toggleColumn}"]`)];
    const next = inputs.some((input) => !input.checked); inputs.forEach((input) => { input.checked = next; });
  }));
})();
