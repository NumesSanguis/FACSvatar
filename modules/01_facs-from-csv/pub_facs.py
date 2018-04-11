"""Publishes FACS (Action Units) and head pos data from an OpenFace .csv

  ZeroMQ:
Default address pub: 127.0.0.1:5570
Pub style: 5 part envelope (including key)
Subscription Key: humanxx
Message parts:
0: sub_key
1: frame
2: timestamp
3: facs
4: head_pose
"""

# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import os
import sys
import six
import time
import glob

import asyncio
import zmq.asyncio
from zmq.asyncio import Context

# own imports
from openfacefiltercsv import FilterCSV


# generator for rows in FACS / head pose dataframe from FilterCSV
class FACSMsgFromCSV:
    def __init__(self,):  # client
        self.filter_csv = FilterCSV

    # generator for FACS and head pose messages
    async def facs_msg_gen(self, file='head_test.csv'):
        # load OpenFace csv as dataframe
        df_csv = FilterCSV(file).df_csv
        print(df_csv.head())

        # get number of rows in dataframe
        df_au_row_count = df_csv.shape[0]
        print("Data rows in data frame: {}".format(df_au_row_count))

        # get current time to match timestamp when publishing
        timer = time.time()

        # send all rows of data 1 by 1
        # message preparation before sleep, then return data
        for frame_tracker in range(df_au_row_count):
            print("FRAME TRACKER: {}".format(frame_tracker))

            #   split data frame
            # FACS data frame
            facs_col = df_csv.columns.str.contains("AU.*_r")
            df_facs = df_csv.loc[:, facs_col]

            # head pose data frame
            head_pose_col = df_csv.columns.str.contains("pose_*")
            df_head_pose = df_csv.loc[:, head_pose_col]

            # get single frame
            row = df_csv.loc[frame_tracker]
            print("frame data: {}\n".format(row))

            # check confidence high enough, else return None as data
            if row['confidence'] < .7:
                facs = None
                head_pose = None

            else:
                # only AU columns
                facs = df_facs.loc[frame_tracker]
                print(facs)

                # only head pose columns
                head_pose = df_head_pose.loc[frame_tracker]
                print(head_pose)

            # # Sleep before sending the messages, so processing time has less influence
            # wait until timer time matches timestamp
            timestamp = row['timestamp']
            time_sleep = timestamp - (time.time() - timer)
            print("waiting {} seconds before sending next FACS".format(time_sleep))

            # don't sleep negative time
            # if time_sleep >= 0:
            #     # currently can send about 3000 fps
            #     await asyncio.sleep(time_sleep)  # time_sleep (~0.031)

            # return msg data; yield in async gen (Python >= 3.6)
            yield row['frame'], timestamp, facs, head_pose

        # return that messages are finished (Python >= 3.6)
        yield None


# goes through 'openface' folder to find latest .csv
class CrawlerCSV:
    # return latest .csv
    def search(self, folder='openface'):
        csv_list = sorted(glob.glob(os.path.join(folder, '*.csv')))

        # # get latest .csv
        # 2nd or higher runmsg_dict
        if csv_list[-1][-10:-4] == "_clean":
            # remove _clean and .csv
            latest_csv = csv_list[-1][:-10]
        else:
            # remove .csv
            latest_csv = csv_list[-1][:-4]

        print("Reading data from: {}".format(latest_csv))

        # return newest .csv file without extension
        return latest_csv


# setup ZeroMQ publisher / subscriber
class NetworkSetup:
    """
    ZeroMQ network setup
    """
    def __init__(self, address='127.0.0.1', port='5570'):
        self.url = "tcp://{}:{}".format(address, port)
        self.ctx = Context.instance()

        # file = CrawlerCSV().search()

        self.facs_csv = FACSMsgFromCSV()

        # activate publishers / subscribers
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.facs_pub(),
        ]))

    # publishes facs values per frame to subscription key 'facs'
    async def facs_pub(self, sub_key='human01'):
        pub = self.ctx.socket(zmq.PUB)
        pub.connect(self.url)
        print("FACS pub initialized")

        # get FACS message
        async for msg in self.facs_csv.facs_msg_gen():
            print(msg)
            # send message if we have data
            if msg:
                # seperate data from meta-data in different envelops
                await pub.send_multipart([sub_key.encode('ascii'),
                                          msg[0],  # frame
                                          msg[1],  # timestamp
                                          msg[2].to_json().encode('utf-8'),  # FACS data; pandas data frame
                                          # TODO separate msg
                                          msg[3].to_json().encode('utf-8')  # head pose data; pandas data frame
                                          ])

            # done
            else:
                print("No more messages to publish; FACS done")

                # tell network messages finished (frame == timestamp == None)
                await pub.send_multipart([sub_key.encode('ascii'), b'', b'', b'', b''])


if __name__ == '__main__':
    # get ZeroMQ version
    print("Current libzmq version is %s" % zmq.zmq_version())
    print("Current  pyzmq version is %s" % zmq.pyzmq_version())

    print("Arguments given: {}".format(sys.argv))
    print("0, 1, or 2 arguments are expected (port, (address)), e.g.: 5570 127.0.0.1")

    # no arguments
    if len(sys.argv) == 1:
        NetworkSetup()

    # local network, only port
    elif len(sys.argv) == 2:
        NetworkSetup(port=sys.argv[1])

    # full network control
    elif len(sys.argv) == 3:
        NetworkSetup(port=sys.argv[1], address=sys.argv[2])

    else:
        print("Received incorrect number of arguments")
