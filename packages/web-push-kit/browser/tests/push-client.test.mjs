import assert from "node:assert/strict";
import test from "node:test";

import { getExistingSubscription, subscribe, supportStatus, unsubscribe } from "../push-client.mjs";

function environment(permission = "granted") {
  return {
    navigator: { serviceWorker: {} },
    PushManager: class {},
    Notification: { requestPermission: async () => permission },
  };
}

test("browser without Push API is unsupported", () => {
  assert.deepEqual(supportStatus({ navigator: {} }), {
    supported: false,
    reason: "service_worker_unavailable",
  });
});

test("denied permission does not create a subscription", async () => {
  let created = false;
  const registration = { pushManager: {
    getSubscription: async () => null,
    subscribe: async () => { created = true; },
  } };
  const result = await subscribe({
    registration,
    publicKey: "QUJD",
    saveSubscription: async () => {},
    environment: environment("denied"),
  });
  assert.equal(result.status, "permission_denied");
  assert.equal(created, false);
});

test("existing subscription is returned and saved", async () => {
  const item = { toJSON: () => ({ endpoint: "https://push.example/existing" }) };
  const registration = { pushManager: { getSubscription: async () => item } };
  assert.equal((await getExistingSubscription(registration)).status, "subscribed");
  let saved;
  const result = await subscribe({
    registration,
    publicKey: "QUJD",
    saveSubscription: async (value) => { saved = value; },
    environment: environment(),
  });
  assert.equal(result.status, "already_subscribed");
  assert.equal(saved.endpoint, "https://push.example/existing");
});

test("new subscription is created and saved", async () => {
  const item = { toJSON: () => ({ endpoint: "https://push.example/new" }) };
  const registration = { pushManager: {
    getSubscription: async () => null,
    subscribe: async () => item,
  } };
  let saved;
  const result = await subscribe({
    registration,
    publicKey: "QUJD",
    saveSubscription: async (value) => { saved = value; },
    environment: environment(),
  });
  assert.equal(result.status, "subscribed");
  assert.equal(saved.endpoint, "https://push.example/new");
});

test("unsubscribe preserves data and informs server", async () => {
  let browserUnsubscribed = false;
  let deleted;
  const item = {
    toJSON: () => ({ endpoint: "https://push.example/remove" }),
    unsubscribe: async () => { browserUnsubscribed = true; return true; },
  };
  const result = await unsubscribe({
    registration: { pushManager: { getSubscription: async () => item } },
    deleteSubscription: async (value) => { deleted = value; },
  });
  assert.equal(result.status, "unsubscribed");
  assert.equal(browserUnsubscribed, true);
  assert.equal(deleted.endpoint, "https://push.example/remove");
});

test("unsubscribe is idempotent when no subscription exists", async () => {
  const result = await unsubscribe({
    registration: { pushManager: { getSubscription: async () => null } },
    deleteSubscription: async () => assert.fail("must not call server callback"),
  });
  assert.equal(result.status, "not_subscribed");
});
