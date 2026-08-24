/** Framework-neutral browser subscription helpers. No function runs automatically. */

export function supportStatus(environment = globalThis) {
  const navigatorObject = environment.navigator;
  if (!navigatorObject || !("serviceWorker" in navigatorObject)) {
    return { supported: false, reason: "service_worker_unavailable" };
  }
  if (!("PushManager" in environment)) {
    return { supported: false, reason: "push_manager_unavailable" };
  }
  if (!("Notification" in environment)) {
    return { supported: false, reason: "notifications_unavailable" };
  }
  return { supported: true, reason: null };
}

export async function registerServiceWorker(scriptUrl, options = {}) {
  const environment = options.environment || globalThis;
  const support = supportStatus(environment);
  if (!support.supported) return { status: "unsupported", reason: support.reason };
  if (typeof scriptUrl !== "string" || !scriptUrl.startsWith("/")) {
    return { status: "error", reason: "service_worker_url_must_be_internal" };
  }
  try {
    const registration = await environment.navigator.serviceWorker.register(scriptUrl, {
      scope: options.scope,
    });
    return { status: "registered", registration };
  } catch (_error) {
    return { status: "error", reason: "service_worker_registration_failed" };
  }
}

export async function getExistingSubscription(registration) {
  if (!registration?.pushManager) return { status: "error", reason: "invalid_registration" };
  try {
    const subscription = await registration.pushManager.getSubscription();
    return subscription
      ? { status: "subscribed", subscription }
      : { status: "not_subscribed", subscription: null };
  } catch (_error) {
    return { status: "error", reason: "subscription_lookup_failed" };
  }
}

export async function subscribe({ registration, publicKey, saveSubscription, environment = globalThis }) {
  if (!registration?.pushManager || typeof saveSubscription !== "function") {
    return { status: "error", reason: "invalid_arguments" };
  }
  const support = supportStatus(environment);
  if (!support.supported) return { status: "unsupported", reason: support.reason };
  // Calling this function must itself be tied to an explicit user gesture.
  let permission;
  try {
    permission = await environment.Notification.requestPermission();
  } catch (_error) {
    return { status: "error", reason: "permission_request_failed" };
  }
  if (permission !== "granted") return { status: "permission_denied", reason: permission };
  try {
    const existing = await registration.pushManager.getSubscription();
    const subscription = existing || await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: decodeBase64Url(publicKey),
    });
    await saveSubscription(subscription.toJSON());
    return { status: existing ? "already_subscribed" : "subscribed", subscription };
  } catch (_error) {
    return { status: "error", reason: "subscription_failed" };
  }
}

export async function unsubscribe({ registration, deleteSubscription }) {
  if (!registration?.pushManager || typeof deleteSubscription !== "function") {
    return { status: "error", reason: "invalid_arguments" };
  }
  try {
    const subscription = await registration.pushManager.getSubscription();
    if (!subscription) return { status: "not_subscribed" };
    // Preserve server-relevant data before the browser invalidates the object.
    const subscriptionData = subscription.toJSON();
    // Remove the authenticated server record first. If the browser operation
    // then fails, the application will still stop sending to this endpoint.
    await deleteSubscription(subscriptionData);
    const removed = await subscription.unsubscribe();
    if (removed === false) return { status: "error", reason: "browser_unsubscription_failed" };
    return { status: "unsubscribed" };
  } catch (_error) {
    return { status: "error", reason: "unsubscription_failed" };
  }
}

export function decodeBase64Url(value) {
  if (typeof value !== "string" || !/^[A-Za-z0-9_-]+={0,2}$/.test(value)) {
    throw new TypeError("publicKey must be base64url encoded");
  }
  const padding = "=".repeat((4 - value.length % 4) % 4);
  const raw = atob((value + padding).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(raw, (character) => character.charCodeAt(0));
}
