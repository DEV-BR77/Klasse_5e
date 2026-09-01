(() => {
  const live = document.querySelector("#live-status");
  const announce = (text) => { if (live) live.textContent = text; };
  const csrf = () => document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] || "";
  document.querySelectorAll("[data-confirm]").forEach((form) => form.addEventListener("submit", (event) => { if (!window.confirm(form.dataset.confirm)) event.preventDefault(); }));
  document.querySelectorAll("[data-dialog-open]").forEach((button) => button.addEventListener("click", () => document.getElementById(button.dataset.dialogOpen)?.showModal()));
  document.querySelectorAll("[data-dialog-close]").forEach((button) => button.addEventListener("click", () => button.closest("dialog")?.close()));

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
