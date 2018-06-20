# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import os
from os.path import join, isfile
import sys
from functools import partial
import argparse
import time
import glob
import json
import asyncio


# FACSvatar imports; if statement for documentation
if __name__ == '__main__':
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
    from openfacefiltercsv import FilterCSV
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ
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

    """

    def __init__(self, csv_arg, csv_folder='openface'):  # client
        self.filter_csv = FilterCSV
        self.csv_list = self.crawl_through_csv(csv_arg, csv_folder)
        print(f"using csv files: {self.csv_list}")
        sys.exit("\ncsv test completed")

    def crawl_through_csv(self, csv_arg, csv_folder):
        print(f"Argument given for csv search: {csv_arg}")
        csv_list = []

        # find specific file if not a number given as argument
        if not csv_arg.isdigit():
            # check file exist
            csv_path = join(csv_folder, csv_arg + ".csv")
            # file exist in 'openface' folder
            if isfile(csv_path):
                csv_list.append([csv_path])

            # TODO if filename contains _P1_ search for P2, P3, P4 etc
            # csv_list[-1].append()

            # file does not exist
            else:
                print(f"File '{csv_arg}' not found in current folder or 'openface'.")

        # if no file selected, get all files
        if not csv_list:
            print(f"Getting list of all csv files in folder '{csv_folder}'...")

            csv_list_all = sorted(glob.glob(join(csv_folder, '*.csv')))
            print(csv_list_all)

            for csv in csv_list_all:
                print(csv)

            # TODO return selection if number argument is given

            # TODO ask which file to run if no number is specified

        return csv_list

    async def msg_gen(self):
        for csv in self.csv_list:
            async for msg in self.msg_from_csv(csv):
                yield msg

    # generator for FACS and head pose messages
    async def msg_from_csv(self, file):
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
        # rename cols from AU**_r to AU**
        df_au_regression.rename(columns=lambda x: x.replace('_r', ''), inplace=True)

        # head pose data frame
        head_pose_col = df_csv.columns.str.contains("pose_*")
        df_head_pose = df_csv.loc[:, head_pose_col]
        # rename cols from pose_* to pitch, roll, yaw
        #df_au_regression.rename({'pose_Rx': 'pitch', 'pose_Ry': 'roll', 'pose_Rz': 'yaw'}, axis='columns', inplace=True)

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
    Future = asyncio.futures.Future

    Crawls through a directory to look for .csv generate by OpenFace
    """

    # return latest .csv
    def search(self, folder='openface'):
        csv_list = sorted(glob.glob(os.path.join(folder, '*.csv')))

        # # get latest .csv
        # 2nd or higher runmsg_dict
        if csv_list[-1][-10:-4] == "_clean":
            # string remove _clean and .csv
            latest_csv = csv_list[-1][:-10]
        else:
            # string remove .csv
            latest_csv = csv_list[-1][:-4]

        print("Reading data from: {}".format(latest_csv))

        # return newest .csv file without extension
        return latest_csv


class FACSvatarMessages(FACSvatarZeroMQ):
    """Publishes FACS and Head movement data from .csv files generated by OpenFace"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # init class to process .csv files
        self.openface_msg = OpenFaceMsgFromCSV(self.misc['csv_arg'], self.misc['csv_folder'])

    # publishes facs values per frame to subscription key 'facs'
    async def facs_pub(self):
        """Calls openface_msg.msg_gen() and publishes returned data"""

        # get FACS message
        async for msg in self.openface_msg.msg_gen():
            print(msg)
            # send message if we have data
            if msg:
                await self.pub_socket.send_multipart([self.pub_key.encode('ascii'),  # topic
                                          msg[0],  # timestamp
                                          msg[1].encode('utf-8')  # data in JSON format or empty byte
                                          ])

            # done
            else:
                print("No more messages to publish; FACS done")

                # tell network messages finished (timestamp == data == None)
                await self.pub_socket.send_multipart([self.pub_key.encode('ascii'), b'', b''])


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--pub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--pub_port", default="5570",
                        help="Port of where to pub to; Default: 5570")
    parser.add_argument("--pub_key", default="openface.offline",
                        help="Key for filtering message; Default: openface.offline")
    parser.add_argument("--pub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")
    parser.add_argument("--csv_arg", default="demo",
                        help="specific csv, -1: show csv list from specified folder, "
                             "0: all csv in specified folder, "
                             ">=1 specific csv file from list")
    parser.add_argument("--csv_folder", default="openface",
                        help="Name of folder with csv files")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))

    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.facs_pub])
