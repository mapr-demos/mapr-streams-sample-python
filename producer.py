#!/usr/bin/env python3
from mapr_streams_python import Producer
import traceback
import sys
import json
import time
"""
This producer will send a bunch of messages to topic "fast-messages". Every so often,
it will send a message to "slow-messages". This shows how messages can be sent to
multiple topics. On the receiving end, we will see both kinds of messages but will
also see how the two topics aren't really synchronized.
"""

TOPIC_FAST_MESSAGES = "fast-messages"
TOPIC_SUMMARY_MARKERS = "summary-markers"
STREAM_SAMPLE = "/sample-stream"
NUMBER_OF_MESSAGES = 10000
FREQUENCY_DIFF_TOPICS = 10

try:
    print("Producing messages...")
    p = Producer({'streams.producer.default.stream': STREAM_SAMPLE})
    count = 0
    total_messages = 0
    for i in range(NUMBER_OF_MESSAGES):
        # Note that the the Java-version of this program uses System.nanoTime() which uses nanoseconds which
        # Python does not natively have. Instead, time.time() is used here which returns a floating point number in
        # seconds. See here for more information: https://docs.python.org/3/library/time.html#time.time.

        data = {'type': 'test',
                't': float("%.3f" % time.time()),
                'k': i}
        p.produce(TOPIC_FAST_MESSAGES, json.dumps(data).encode('utf-8'))
        count += 1
        total_messages += 1

        if i % FREQUENCY_DIFF_TOPICS == 0:
            data_fast = {'type': 'marker',
                         't': float("%.3f" % time.time()),
                         'k': i}

            p.produce(TOPIC_FAST_MESSAGES, json.dumps(data_fast).encode('utf-8'))
            count += 1
            total_messages += 1

            data_summary = {'type': 'other',
                            't': float("%.3f" % time.time()),
                            'k': i}

            p.produce(TOPIC_SUMMARY_MARKERS, json.dumps(data_summary).encode('utf-8'))
            count += 1
            total_messages += 1

            p.flush()

        # Note this output is slightly different than the Java-version of this program to help improve
        # understanding and readability
        print("Sent {count} messages this round out of {total} sent so far".format(count=count, total=total_messages))
        count = 0  # Reset count at end of loop
    print("Done!")
except Exception as e:
    print("*** Exception occurred:")
    traceback.print_exc(file=sys.stdout)