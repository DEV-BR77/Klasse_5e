/* Copy this classic worker and set WEB_PUSH_ALLOWED_ORIGINS before deployment if needed. */
const WEB_PUSH_ALLOWED_ORIGINS = [];
const MAX_ACTIONS = 2;

function allowedTarget(rawUrl) {
  if (typeof rawUrl !== "string" || !rawUrl || rawUrl.startsWith("//")) return null;
  try {
    const target = new URL(rawUrl, self.location.origin);
    const allowed = new Set([self.location.origin, ...WEB_PUSH_ALLOWED_ORIGINS]);
    if (target.protocol !== "https:" || !allowed.has(target.origin)) return null;
    return target.href;
  } catch (_error) {
    return null;
  }
}

function validPayload(data) {
  if (!data || typeof data !== "object") return null;
  for (const field of ["title", "body", "url", "category", "message_id"]) {
    if (typeof data[field] !== "string" || !data[field]) return null;
  }
  const target = allowedTarget(data.url);
  if (!target) return null;
  const actions = Array.isArray(data.actions) ? data.actions.slice(0, MAX_ACTIONS).filter((action) => (
    action && typeof action.action === "string" && action.action &&
    typeof action.title === "string" && action.title &&
    (!action.url || allowedTarget(action.url))
  )) : [];
  return { ...data, target, actions };
}

self.addEventListener("push", (event) => {
  let raw;
  try { raw = event.data?.json(); } catch (_error) { raw = null; }
  const data = validPayload(raw);
  if (!data) return;
  event.waitUntil(self.registration.showNotification(data.title, {
    body: data.body,
    tag: data.tag || data.message_id,
    icon: data.icon && allowedTarget(data.icon) ? data.icon : undefined,
    actions: data.actions.map(({ action, title }) => ({ action, title })),
    data,
  }));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const data = validPayload(event.notification.data);
  if (!data) return;
  const action = data.actions.find((candidate) => candidate.action === event.action);
  const target = allowedTarget(action?.url || data.target);
  if (!target) return;
  event.waitUntil((async () => {
    const windows = await clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const windowClient of windows) {
      if (new URL(windowClient.url).origin === new URL(target).origin && "focus" in windowClient) {
        if ("navigate" in windowClient) await windowClient.navigate(target);
        return windowClient.focus();
      }
    }
    return clients.openWindow(target);
  })());
});

// pushsubscriptionchange is intentionally not used as a reliability mechanism.
// The application should call getExistingSubscription/subscribe on a normal visit.
