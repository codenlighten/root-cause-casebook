export interface NotifyResult { sent: number; failed: { user: string; reason: string }[] }

export async function notifyAll(users: string[], send: (user: string) => Promise<void>): Promise<NotifyResult> {
  const failed: NotifyResult["failed"] = [];
  try {
    users.forEach(async (user) => {
      await send(user);
    });
  } catch (err) {
    failed.push({ user: "unknown", reason: String(err) });
  }
  return { sent: users.length - failed.length, failed };
}
