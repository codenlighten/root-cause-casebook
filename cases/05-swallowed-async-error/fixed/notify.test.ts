import { test } from "node:test";
import assert from "node:assert/strict";
import { notifyAll } from "./notify.ts";

test("a failed send is reported, and the other sends still happen", async () => {
  const delivered: string[] = [];
  const send = async (user: string): Promise<void> => {
    await new Promise((resolve) => setTimeout(resolve, 5));
    if (user === "bob") throw new Error("mailbox full");
    delivered.push(user);
  };

  const result = await notifyAll(["ann", "bob", "cy"], send);

  assert.deepEqual(result.failed, [{ user: "bob", reason: "mailbox full" }]);
  assert.equal(result.sent, 2);
  assert.deepEqual(delivered.sort(), ["ann", "cy"]);
});

test("when everything succeeds nothing is reported as failed", async () => {
  const result = await notifyAll(["ann"], async () => {});
  assert.deepEqual(result, { sent: 1, failed: [] });
});
