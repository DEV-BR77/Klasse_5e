import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

function workerHarness() {
  const handlers = {};
  const opened = [];
  const focused = [];
  const context = {
    URL,
    self: {
      location: { origin: "https://class.example.test" },
      registration: { showNotification: async () => {} },
      addEventListener: (name, handler) => { handlers[name] = handler; },
    },
    clients: {
      matchAll: async () => [{
        url: "https://class.example.test/current",
        navigate: async (url) => opened.push(url),
        focus: async () => focused.push(true),
      }],
      openWindow: async (url) => opened.push(url),
    },
  };
  vm.runInNewContext(fs.readFileSync(new URL("../service-worker.js", import.meta.url), "utf8"), context);
  return { handlers, opened, focused };
}

function clickEvent(data, action = "") {
  let promise;
  return {
    notification: { data, close() {} },
    action,
    waitUntil(value) { promise = value; },
    complete: async () => promise,
  };
}

test("notification click focuses an existing window for a valid internal URL", async () => {
  const harness = workerHarness();
  const event = clickEvent({
    title: "Titel", body: "Text", url: "/messages/1", category: "general", message_id: "m1",
  });
  harness.handlers.notificationclick(event);
  await event.complete();
  assert.equal(harness.focused.length, 1);
  assert.equal(harness.opened[0], "https://class.example.test/messages/1");
});

test("notification click rejects an unconfigured external URL", async () => {
  const harness = workerHarness();
  const event = clickEvent({
    title: "Titel", body: "Text", url: "https://attacker.example/", category: "general", message_id: "m1",
  });
  harness.handlers.notificationclick(event);
  await event.complete();
  assert.deepEqual(harness.opened, []);
  assert.deepEqual(harness.focused, []);
});
