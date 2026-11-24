"""One Word for Your Wi-Fi.

Writes a single word describing my Wi-Fi to entry.txt: the word that
captures how home Wi-Fi actually behaves. Full bars, "Connected",
and yet nothing loads -- the router insists everything is fine while
quietly refusing to serve a single byte. It tells you you're online
while denying you the internet. That is not a connection, it is
gaslighting, and the word carries the whole joke on its own.
"""

import os
import stat
import tempfile

WORD = "Gaslighting"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")

    data = WORD.encode("utf-8")

    # Self-check: exactly one word -- no whitespace at all, single token,
    # and inside the gate's 1-20 character window.
    text = data.decode("utf-8")
    assert 1 <= len(text) <= 20, "word outside 1-20 characters"
    assert text.isalpha(), "a single word needs no punctuation"
    assert text.split() == [text], "output must be exactly one word"
    assert not any(ch.isspace() for ch in text), "no whitespace allowed"

    # Atomic write via temp file + rename, world-readable 0644.
    # The temp file is created in the same directory so the rename
    # never crosses filesystems.
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    # Read back and verify: bytes match exactly, no trailing newline,
    # mode 0644.
    with open(target, "rb") as f:
        actual = f.read()
    assert actual == data, "read-back mismatch"
    assert not actual.endswith(b"\n"), "no trailing newline allowed"
    mode = stat.S_IMODE(os.stat(target).st_mode)
    assert mode == 0o644, "output must be mode 0644, got %o" % mode


if __name__ == "__main__":
    main()
