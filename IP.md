# IP records

| Date | Covers | Type | Record hash | Signer | Tag |
|---|---|---|---|---|---|
| 2026-11-26 | Commit `92f57a1`: nine constructed bugs in five languages with fixes, regression tests and write-ups. No authorship claimed in the language toolchains and third-party libraries. | software, hash-only | [`0a526409907a5c223e31581782ef76c88a535dcd3c9f190c9e0de509b56c32be`](https://iptrust.org/v/0a526409907a5c223e31581782ef76c88a535dcd3c9f190c9e0de509b56c32be) | Gregory J. Ward | `ip-2026-11-26` |
| 2026-11-26 | Commit `1049d5b`: nine constructed bugs in five languages with fixes, regression tests and write-ups; revision correcting several fixed cases and their tests. No authorship claimed in the language toolchains and third-party libraries. | software, hash-only | [`11bceea05b438cae2a2008ecb46c1c74a2e42276f585b2fddd4a61d790046438`](https://iptrust.org/v/11bceea05b438cae2a2008ecb46c1c74a2e42276f585b2fddd4a61d790046438) | Gregory J. Ward | `ip-2026-11-26-2` |

A record is evidence that the committed content existed by the time of its anchor and that the signer made
the statement; it does not create or register any right. Anchoring completes some hours after submission.
Files under `third_party/`, where present, are not part of the record.

## Verifying

The commands below show the first record. For a later one, use its record hash and tag from the table.

Verification needs the evidence package for the record, which the author holds and which is not committed
here. With it in `.iptrust/`:

```
git worktree add /tmp/at-tag-root-cause-casebook ip-2026-11-26
cp -r .iptrust /tmp/at-tag-root-cause-casebook/
(cd /tmp/at-tag-root-cause-casebook && iptrust2 verify 0a526409907a5c223e31581782ef76c88a535dcd3c9f190c9e0de509b56c32be --fetch-headers)
git worktree remove --force /tmp/at-tag-root-cause-casebook
```

Expect `verdict: valid` and `content: matched` once both chains have anchored.
