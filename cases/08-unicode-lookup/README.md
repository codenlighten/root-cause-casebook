# 08. "José is not in the directory" when he is (Python)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom

"Searching for José García finds nothing when I paste the name from a PDF, but it works when I type it. Searching 'STRASSE Café' does not find 'Straße Café'."

## Reproduce

```bash
./run-case.sh 8
```

## Investigation

1. **Compare the two strings.** Both print as "José García" and `==` returned `False`. A visually identical, unequal pair means different code points.
2. **Look at the code points.** Typed: `J o s 0xe9`. Pasted: `J o s 0x65 0x301`, an "e" followed by a combining acute accent. Both are valid spellings of the same letter (NFC and NFD).
3. **Hypothesis: whitespace or encoding differences.** Rejected. `strip()` made no difference, and both strings decode as valid UTF-8.
4. **Test the second report separately.** `"straße".lower()` is `straße`, but `"STRASSE".lower()` is `strasse`: lowercasing does not equate them, and `casefold()` (`strasse`) does. This is a separate cause, which is why the test has separate checks for it.
5. **Check the negative case.** "Jose Garcia" without accents should not match "José García". Those are different spellings, so the fix must not strip accents.

## Root cause

Names were compared after `lower()` only: that neither canonicalizes composed against decomposed characters nor handles full case folding, so equal text with different code points missed.

## Fix

One key function used by both `add` and `find`: `unicodedata.normalize("NFC", s.strip()).casefold()`.

## Why the regression test would have caught it

It uses the decomposed spelling (written as escapes, so an editor cannot silently normalize the test file) and the sharp-s case, plus an unrelated negative case. Deliberate break: removing only the NFC step fails the decomposed-name test and leaves the sharp-s test passing, so each part of the fix is guarded by its own test.

## How to spot this class next time

- "Looks identical, compares unequal" means print the code points (`[hex(ord(c)) for c in s]`).
- Normalise text once, at the boundary, in one function used on both sides of a comparison.
- Use `casefold`, not `lower`, for caseless matching, and write non-ASCII test data as escapes.

## Limits

This is NFC plus casefold. It does not handle locale rules such as the Turkish dotless i, nor compatibility forms (NFKC), such as full-width letters, and it deliberately does not remove accents.
