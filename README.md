# Sample Programs for MapR Streams in Python

This project provides a simple but realistic example of a Kafka
producer and consumer compatible with MapR Streams while using Python.

This project is a Python version of the [Java MapR Sample Programs for MapR Streams](https://github.com/mapr-demos/mapr-streams-sample-programs).

The application logic is slightly different since this is in Python instead of Java, but the conceptual logic is still the same.


## Prerequisites
1. To start, you need to get a **MapR 5.2** running. You can install your [own cluster](https://mapr.com/download/) or [download a sandbox](https://mapr.com/products/mapr-sandbox-hadoop/download/).
    * **NOTE**: In this example, we used the MapR 5.2 Sandbox via VirtualBox.
2. Your MapR test node or local machine running these Python scripts must have **Python 3.6**
3. Create and activate a Python **virtualenv** in either Mac OS X or Linux
    ```
    $ python3.6 -m venv --system-site-packages ~/maprstreams
    $ source ~/maprstreams/bin/activate
    ```
4. Install the **mapr-client** package per [the instructions for your operating system](http://maprdocs.mapr.com/home/AdvancedInstallation/SettingUptheClient-install-mapr-client.html)
5. Install the **mapr-librdkafka** package per [the instructions for your operating system](http://maprdocs.mapr.com/home/AdvancedInstallation/InstallingStreamsCClient.html)
    1. Ensure you set the **DYLD_LIBRARY_PATH** or **LD_LIBRARY_PATH** in the ```activate``` script of your virtualenv per the instructions for [Configuring the MapR Streams C Client](http://maprdocs.mapr.com/home/MapR_Streams/MapRStreamCAPISetup.html#task_qxg_h2m_3z)
    * **NOTE for OS X users only:** Setting this environment variable will only work in your virtualenv on Mac OS X; it will not be recognized from your .bash_profile due to OS X's security policy or from PyCharm.
6. For Mac OS X or Linux users, install the [MapR Python client](http://maprdocs.mapr.com/home/AdvancedInstallation/InstallingStreamsPYClient.html) per below:
    ```
    $ source ~/maprstreams/bin/activate
    $ pip3 install mapr-streams-python --user
    ```
7. Download and unzip, or clone, **this repository** to your local machine
8. Install this project's **requirements**:
    ```
    $ source ~/maprstreams/bin/activate
    $ export PYTHONUSERBASE=$VIRTUAL_ENV
    $ cd <directory_of_this_example_programs_files>
    $ pip3 install -r requirements.txt --user
    ```
## Dependencies

You will also need these Python modules which will be installed from the ```requirements.txt``` file:
```
future==0.16.0
hdrhistogram==0.5.2
mapr-streams-python==0.9.2
```
## Step 1: Create the stream

A *stream* is a collection of topics that you can manage together for security, default number or partitions, and time to leave for the messages.

Run the following command on your MapR cluster:

```
$ maprcli stream create -path /sample-stream
```

By default the produce and consume topic permission are defaulted to the creator of the streams, the unix user you are using to run the `maprcli` command.

It is possible to configure the permission by editing the streams, for example to make all the topic available to anybody (public permission) you can run the following command:

```
maprcli stream edit -path /sample-stream -produceperm p -consumeperm p -topicperm p
```

This is useful for this example since we want to run the producer and consumer from remote computers too.

## Step 2: Create the topics

We need two topics for the example program, that are also created with the `maprcli` tool
```
$ maprcli stream topic create -path /sample-stream  -topic fast-messages
$ maprcli stream topic create -path /sample-stream  -topic summary-markers
```

These can be listed
```
$ maprcli stream topic list -path /sample-stream
topic            partitions  logicalsize  consumers  maxlag  physicalsize
fast-messages    1           0            0          0       0
summary-markers  1           0            0          0       0
```

Note that the program will automatically create the topic if it does not already exist.


## Step 3: Run the example producer

The producer will send a large number of messages to `/sample-stream:fast-messages`
along with occasional messages to `/sample-stream:summary-markers`. Since there isn't
any consumer running yet, nobody will receive the messages. 

So you can run the application using the following commands:

```
$ source ~/maprstreams/bin/activate
$ cd <directory_of_this_example_programs_files>
$ python producer.py
Sent 1 messages this round out of 10018 sent so far
Sent 1 messages this round out of 10019 sent so far
Sent 1 messages this round out of 10020 sent so far
...
Sent 3 messages this round out of 10023 sent so far
```

The only important difference here between an Apache Kafka application and MapR Streams application is that the client libraries are different. This causes the MapR Producer to connect to the MapR cluster to post the messages, and not to a Kafka broker.


## Step 4: Start the example consumer

In a terminal window, you can run the consumer using the following command:

```
$ source ~/maprstreams/bin/activate
$ cd <directory_of_this_example_programs_files>
$ python consumer.py
Got 1 records after 0 timeouts
Got 1 records after 0 timeouts
1000 messages received in period, latency(min, max, avg, 99%) = 10, 17, 13.207, 16 (sec)
1000 messages received in overall, latency(min, max, avg, 99%) = 10, 17, 13.207, 16 (sec)
...
Got 1 records after 0 timeouts
```


Note that there is a latency listed in the summaries for the message batches.
This is because the consumer wasn't running when the message were sent to Kafka and thus
it is only getting them much later, long after they were sent.

The consumer should, however, gnaw its way through the backlog pretty quickly,
however and the per batch latency should be shorter by the end of the run than at the beginning.

If the producer is still running by the time the consumer catches up, the latencies will probably
drop into the single digit second range.


## Monitoring your topics

At any time you can use the `maprcli` tool to get some information about the topic, for example:

```
$ maprcli stream topic info -path /sample-stream -topic fast-messages -json
```
`-json` is just use to get the topic information as a JSON document.


## Cleaning Up

When you are done playing, you can delete the stream, and all associated topic using the following command:
```
$ maprcli stream delete -path /sample-stream
```



## From Apache Kafka to MapR Streams

1. The topics have moved from `"fast-messages"` to `"/sample-stream:fast-messages"` and `"summary-markers"` to `"/sample-stream:summary-markers"`
2. The [producer](http://maprdocs.mapr.com/52/index.html#MapR_Streams/configuration_parameters_for_producers.html) and [consumer](http://maprdocs.mapr.com/52/index.html#MapR_Streams/configuration_parameters_for_consumers.html) configuration parameters that are not used by MapR Streams are automatically ignored
3. The producer and Consumer applications are executed with the dependencies of a MapR Client not Apache Kafka.

That's it!


## Credits
Note that this example was derived in part from the documentation provided by the Apache Kafka project. We have 
added short, realistic sample programs that illustrate how real programs are written using MapR Streams.
