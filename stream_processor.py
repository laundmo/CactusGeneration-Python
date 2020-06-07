"""
All credit goes to
https://stackoverflow.com/a/54196835/5997749

i simply modified it to properly return and use ProcessPoolExecutor instead - laundmo
"""

import logging
import queue
import signal
import sys
import time
from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED

level = logging.DEBUG
log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
handler.setLevel(level)
log.addHandler(handler)
log.setLevel(level)

WAIT_SLEEP = 1  # second, adjust this based on the timescale of your tasks

class BufferedIter(object):
    def __init__(self, iterator):
        self.iter = iterator

    def nextN(self, n):
        vals = []
        for _ in range(n):
            vals.append(next(self.iter))
        return vals


def stream_processor(input_stream, task, num_workers):

    # Use a queue to signal shutdown.
    shutting_down = queue.Queue()

    def shutdown(signum, frame):
        log.warning('Caught signal %d, shutting down gracefully ...' % signum)
        # Put an item in the shutting down queue to signal shutdown.
        shutting_down.put(None)

    # Register the signal handler
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    def is_shutting_down():
        return not shutting_down.empty()

    futures = dict()
    buffer = BufferedIter(input_stream)
    with ProcessPoolExecutor(num_workers) as executor:
        num_success = 0
        num_failure = 0
        while True:
            idle_workers = num_workers - len(futures)

            if not is_shutting_down():
                items = buffer.nextN(idle_workers)
                for data in items:
                    futures[executor.submit(task, data)] = data

            done, _ = wait(futures, timeout=WAIT_SLEEP, return_when=ALL_COMPLETED)
            for f in done:
                data = futures[f]
                try:
                    yield (f.result(), data)
                except Exception as exc:
                    #log.error('future encountered an exception: %r, %s' % (data, exc))
                    num_failure += 1
                else:
                    #log.info('future finished successfully: %r' % data)
                    num_success += 1

                del futures[f]

            if is_shutting_down() and len(futures) == 0:
                break

        log.info("num_success=%d, num_failure=%d" % (num_success, num_failure))