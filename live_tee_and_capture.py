# Copyright (c) 2026 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import sys
from os import close, pipe, read, write
from threading import Thread
from typing import Sequence, Text, Tuple
from ctypes_unicode_proclaunch import launch, wait
from threading_value_event import ThreadingValueEvent


def fd_teeing_worker(read_fd, write_fd, buf):
    while True:
        byte = read(read_fd, 1)
        if not byte:
            break
        write(write_fd, byte)
        buf.extend(byte)


def fd_reading_worker(read_fd, buf):
    while True:
        byte = read(read_fd, 1)
        if not byte:
            break
        buf.extend(byte)


def exit_code_capturing_worker(
        pid,
        exit_code_event,  # type: ThreadingValueEvent[int]
):
    try:
        retval = wait(pid)
        exit_code_event.set(retval)
    except OSError:
        pass


def live_tee_and_capture(
        command,  # type: Sequence[Text]
        tee_stdout=True,  # type: bool
        tee_stderr=True,  # type: bool
):
    # type: (...) -> Tuple[int, bytearray, bytearray]
    exit_code_event = ThreadingValueEvent()

    stdout_r, stdout_w = pipe()
    stderr_r, stderr_w = pipe()

    stdout_buffer = bytearray()
    stderr_buffer = bytearray()

    if tee_stdout:
        stdout_reading_thread = Thread(target=fd_teeing_worker, args=(stdout_r, sys.stdout.fileno(), stdout_buffer))
    else:
        stdout_reading_thread = Thread(target=fd_reading_worker, args=(stdout_r, stdout_buffer))
    stdout_reading_thread.start()

    if tee_stderr:
        stderr_reading_thread = Thread(target=fd_teeing_worker, args=(stderr_r, sys.stderr.fileno(), stderr_buffer))
    else:
        stderr_reading_thread = Thread(target=fd_reading_worker, args=(stderr_r, stderr_buffer))
    stderr_reading_thread.start()

    pid = launch(command, stdout_file_descriptor=stdout_w, stderr_file_descriptor=stderr_w)

    exit_code_capturing_thread = Thread(target=exit_code_capturing_worker, args=(pid, exit_code_event))
    exit_code_capturing_thread.start()

    exit_code = exit_code_event.wait()

    exit_code_capturing_thread.join()
    close(stdout_w)
    close(stderr_w)

    stdout_reading_thread.join()
    close(stdout_r)

    stderr_reading_thread.join()
    close(stderr_r)

    return exit_code, stdout_buffer, stderr_buffer
