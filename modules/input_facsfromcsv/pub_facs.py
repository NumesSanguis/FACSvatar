# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import os
import sys
import six
import time
import glob
import json

import asyncio
import zmq.asyncio
from zmq.asyncio import Context

# own imports; if statement for documentation
if __name__ == '__main__':
    from openfacefiltercsv import FilterCSV
else:
    from .openfacefiltercsv import FilterCSV


# class OpenFaceMessage:
#     def __init__(self, timestamp=b'', frame_no=b'', confidence=b'', pose=b'', gaze=b'', au_regression=b''):
#         self.timestamp = timestamp
#         self.frame_no = frame_no
#         self.confidence = confidence
#         self.pose = pose
#         self.gaze = gaze
#         self.au_regression = au_regression


# generator for rows in FACS / head pose dataframe from FilterCSV
class OpenFaceMsgFromCSV:
    """
    Publishes FACS (Action Units) and head pos data from an OpenFace .csv

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

    def __init__(self,):  # client
        self.filter_csv = FilterCSV

    # generator for FACS and head pose messages
    async def msg_gen(self, file='demo.csv'):
        """
        Generates messages from a csv file

        :param file: path + file name of csv file
        :return: data of a message to be send in JSON
        """

        # load OpenFace csv as dataframe
        df_csv = FilterCSV(file).df_csv
        print(df_csv.head())

        # get number of rows in dataframe
        df_au_row_count = df_csv.shape[0]
        print("Data rows in data frame: {}".format(df_au_row_count))

        #   split data frame
        # au_regression data frame
        au_regression_col = df_csv.columns.str.contains("AU.*_r")
        df_au_regression = df_csv.loc[:, au_regression_col]

        # head pose data frame
        head_pose_col = df_csv.columns.str.contains("pose_*")
        df_head_pose = df_csv.loc[:, head_pose_col]

        # get current time to match timestamp when publishing
        timer = time.time()

        # send all rows of data 1 by 1
        # message preparation before sleep, then return data
        for frame_tracker in range(df_au_row_count):
            print("FRAME TRACKER: {}".format(frame_tracker))

            # get single frame
            row = df_csv.loc[frame_tracker]
            # print("frame data: {}\n".format(row))
            timestamp = row['timestamp']

            # check confidence high enough, else return None as data
            if row['confidence'] < .7:
                yield timestamp, b''

            else:
                # init a message dict
                msg = dict()

                # metadata in message
                msg['frame'] = row['frame']
                msg['timestamp'] = timestamp

                # au_regression in message as JSON
                msg['au_r'] = df_au_regression.loc[frame_tracker].to_dict()
                # print(msg['au_r'])

                # head pose in message as JSON
                msg['pose'] = df_head_pose.loc[frame_tracker].to_dict()
                # print(msg['pose'])

                # # Sleep before sending the messages, so processing time has less influence
                # wait until timer time matches timestamp
                time_sleep = timestamp - (time.time() - timer)
                print("waiting {} seconds before sending next message".format(time_sleep))

                # don't sleep negative time
                if time_sleep >= 0:
                    # currently can send about 3000 fps
                    await asyncio.sleep(time_sleep)  # time_sleep (~0.031)

                # return msg data; yield in async gen (Python >= 3.6)
                yield timestamp, json.dumps(msg)  # .__dict__

        # return that messages are finished (Python >= 3.6)
        yield None


# goes through 'openface' folder to find latest .csv
class CrawlerCSV:
    """
    Crawls through a directory to look for .csv generate by OpenFace
    """

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

        self.openface_msg = OpenFaceMsgFromCSV()

        # activate publishers / subscribers
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.facs_pub(),
        ]))

    # publishes facs values per frame to subscription key 'facs'
    async def facs_pub(self, sub_key='openface_offline'):
        pub = self.ctx.socket(zmq.PUB)
        pub.connect(self.url)
        print("FACS pub initialized")

        # get FACS message
        async for msg in self.openface_msg.msg_gen():
            print(msg)
            # send message if we have data
            if msg:
                # seperate data from meta-data in different envelops
                # await pub.send_multipart([sub_key.encode('ascii'),
                #                           msg[0],  # frame
                #                           msg[1],  # timestamp
                #                           msg[2].to_json().encode('utf-8'),  # FACS data; pandas data frame
                #                           # TODO separate msg
                #                           msg[3].to_json().encode('utf-8')  # head pose data; pandas data frame
                #                           ])
                await pub.send_multipart([sub_key.encode('ascii'),  # topic
                                          msg[0],  # timestamp
                                          msg[1].encode('utf-8')  # data in JSON format or empty byte
                                          ])

            # done
            else:
                print("No more messages to publish; FACS done")

                # tell network messages finished (timestamp == data == None)
                await pub.send_multipart([sub_key.encode('ascii'), b'', b''])


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
