from __future__ import print_function

import os
import stat
import tempfile

import itertools
import subprocess
import threading
import contextlib

DIFF = "diff"
DIFF_EDITOR = "vimdiff"

@contextlib.contextmanager
def get_fifo():
    filename = tempfile.mktemp()
    os.mkfifo(filename, 0o600)
    try:
        yield (filename, filename)
    finally:
        os.unlink(filename)

def _write_to_fifo(fifo, input_data):
    with open(fifo, "w") as f:
        f.write(input_data)

def diff(old, new, labels=["old", "new"]):
    with get_fifo() as fifo1, get_fifo() as fifo2:
        t1 = threading.Thread(target=_write_to_fifo, args=(fifo1[1], old.encode("UTF-8")))
        t2 = threading.Thread(target=_write_to_fifo, args=(fifo2[1], new.encode("UTF-8")))

        t1.start()
        t2.start()

        args = [DIFF, "-u"]
        if labels:
            args.extend(["--label", labels[0], "--label", labels[1]])
        args.extend([fifo1[0], fifo2[0]])

        subprocess.call(args)

        t1.join()
        t2.join()

def run_diff_editor(texts, labels=None):
    if not isinstance(texts, list):
        raise TypeError

    if labels is None:
        labels = [""] * len(texts)

    if not isinstance(labels, list):
        raise TypeError

    open_files = []
    try:
        for text, label in itertools.izip(texts, labels):
            f = tempfile.NamedTemporaryFile(mode="w+", suffix="_" + label + ".txt")
            open_files.append(f)
            
            f.write(text.encode("UTF-8"))
            f.flush()

        subprocess.call([DIFF_EDITOR] + [f.name for f in open_files])

        open_files[0].seek(0)
        return open_files[0].read().decode("UTF-8")
    finally:
        for f in open_files:
            try:
                f.close()
            except Exception as e:
                print(e, file=sys.stderr)

if __name__ == "__main__":
    def main():
        print(`run_diff_editor(["lol\n", "lol\nlol\n"], ["old", "new"])`)

    main()
