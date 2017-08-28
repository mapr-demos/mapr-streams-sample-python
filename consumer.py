#!/usr/bin/env python3
from mapr_streams_python import Consumer, KafkaError
import json
import time
from hdrh.histogram import HdrHistogram

# Variables identfiying name of streams and topics
TOPIC_FAST_MESSAGES = "/sample-stream:fast-messages";
TOPIC_SUMMARY_MARKERS = "/sample-stream:summary-markers";

print("Consuming messages...")
c = Consumer({'group.id': 'mygroup',
              'default.topic.config': {'auto.offset.reset': 'earliest'},
              'auto.commit.interval.ms': 500})
c.subscribe([TOPIC_FAST_MESSAGES, TOPIC_SUMMARY_MARKERS])

# Note that:
# - The 3 is for significant figures but only applies when using HdrHistogram's output_percentile_distribution
# function
# - HdrHistogram for Python only works with integers (not decimals)
stats_periodic = HdrHistogram(1, 10000000, 3)
stats_all = HdrHistogram(1, 10000000, 3)

timeouts = 0
records = 0
running = True
try:
    while running:
        msg = c.poll(timeout=0.200)
        if msg is None:
            timeouts += 1
            continue
        if not msg.error():
            records += 1
            print("Got {records} records after {timeouts} timeouts".format(records=records, timeouts=timeouts))
            timeouts = 0
            records = 0

            # msg_value is expected in this format:
            # {'k': 0, 't': '1.503', 'type': 'test'}
            # Note that we do not explicitly call .decode('utf-8') on msg.value() because json.loads expects the intput
            # to already be encoded (as of Python 3.6)
            msg_value = json.loads(msg.value())

            if msg.topic() == TOPIC_FAST_MESSAGES:
                # the send time is encoded in side the message
                if msg_value.get('type', '') == "test":
                    latency = float("%.3f" % time.time()) - msg_value.get('t', 0)
                    stats_periodic.record_value(latency)
                    stats_all.record_value(latency)
                elif msg_value.get('type', '') == "marker":
                    # whenever we get a marker message, we should dump out the stats
                    # note that the number of fast messages won't necessarily be quite constant
                    print(
                        "{numbermsgs} messages received in period, latency(min, max, avg, 99%) = "
                        "{latency_min}, {latency_max}, {latency_avg}, {latency_percentile} (sec)".format(
                            numbermsgs=stats_periodic.get_total_count(),
                            latency_min=stats_periodic.get_value_at_percentile(0),
                            latency_max=stats_periodic.get_value_at_percentile(100),
                            latency_avg=stats_periodic.get_mean_value(),
                            latency_percentile=stats_periodic.get_value_at_percentile(99)))
                    print(
                        "{numbermsgs} messages received in overall, latency(min, max, avg, 99%) = "
                        "{latency_min}, {latency_max}, {latency_avg}, {latency_percentile} (sec)".format(
                            numbermsgs=stats_all.get_total_count(),
                            latency_min=stats_all.get_value_at_percentile(0),
                            latency_max=stats_all.get_value_at_percentile(100),
                            latency_avg=stats_all.get_mean_value(),
                            latency_percentile=stats_all.get_value_at_percentile(99)))
                    stats_periodic.reset()
                else:
                    print("Illegal message type: " + msg_value.get('type', ''))
            elif msg.topic() != TOPIC_SUMMARY_MARKERS:
                # do nothing with TOPIC_SUMMARY_MARKERS at this level but report if unknown topic emerges
                print("Shouldn't be possible to get message on topic {topic}" + msg.topic())

        elif msg.error().code() != KafkaError._PARTITION_EOF:
            print(msg.error())
            running = False

except KeyboardInterrupt:
    print("You pressed Ctrl+C. Closing Consumer gracefully.")

c.close()
print("Done!")
