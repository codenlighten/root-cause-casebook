export interface NotifyResult { sent: number; failed: { user: string; reason: string }[] }

export async function notifyAll(users: string[], send: (user: string) => Promise<void>): Promise<NotifyResult> {
  const outcomes = await Promise.allSettled(users.map((user) => send(user)));
  const failed: NotifyResult["failed"] = [];
  outcomes.forEach((outcome, i) => {
    if (outcome.status === "rejected") {
      const reason = outcome.reason instanceof Error ? outcome.reason.message : String(outcome.reason);
      failed.push({ user: users[i], reason });
    }
  });
  return { sent: users.length - failed.length, failed };
}
