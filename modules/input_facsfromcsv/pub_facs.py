"""Prepossesses openface .csv files and publishes its data to FACSvatar

Relies on Python 3.6+ due to async generator yield statement"""

# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import os
# from os.path import join, isfile
from pathlib import Path
import sys
# from functools import partial
import argparse
import time
# import glob
import json
import asyncio
import pandas as pd


# FACSvatar imports; if statement for documentation
if __name__ == '__main__':
    # TODO work irrespectively of folder
    # sys.path.append(".")
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
    from openfacefiltercsv import FilterCSV
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ
    from .openfacefiltercsv import FilterCSV


# goes through 'openface' folder to find latest .csv
class CrawlerCSV:
    """Crawls through a directory to look for .csv generate by OpenFace and the already cleaned versions

    Filenames with _P* are messaged together
    """

    def __init__(self):
        self.filter_csv = FilterCSV()

    # returns list of .csv files used for generating messages
    def gather_csv_list(self, csv_folder_raw, csv_arg):
        csv_folder_raw = Path(csv_folder_raw)

        # get all csv files in folder raw
        csv_raw = self.search_csv(csv_folder_raw)
        print(csv_raw)
        # folder not found, return empty list
        # if not csv_raw:
        #     return []

        # rename folder to folder_clean
        csv_folder_clean = csv_folder_raw.parent / (csv_folder_raw.parts[-1] + '_clean')
        # get all csv files in folder clean
        csv_clean = self.search_csv(csv_folder_clean)

        # raw and clean folder not found, return empty list
        if not csv_raw and not csv_clean:
            return []

        # perform cleaning on files in raw that have not been cleaned yet
        for raw in csv_raw:
            # no cleaned file exist
            if raw not in csv_clean:
                # call clean on csv and save in clean folder
                self.filter_csv.clean_controller(csv_folder_raw / raw, csv_folder_clean)
                # self.filter_csv()

        #   use argument to determine which csv files will be returned for message generation
        csv_message_list = []
        # find specific file if file name and not a number is given as argument
        if not csv_arg.isdigit() and (csv_arg != '-1') and (csv_arg != '-2'):
            print(f"\nFile is given as argument: {csv_arg}")
            csv_message_list = [sorted(self.search_csv(csv_folder_clean, csv_arg, True))]

        # number is given as argument
        else:
            csv_arg = int(csv_arg)
            print(f"Number is given as argument: {csv_arg}")
            # get all cleaned csv, including new ones
            csv_all_clean = sorted(self.search_csv(csv_folder_clean, "*", True))

            # files were found
            if csv_all_clean:
                print(f"All files found in {csv_folder_clean}")
                no_files = len(csv_all_clean)
                for i, csv in enumerate(csv_all_clean):
                    print(f"[{i}] {csv.name}")

                # return all files
                if csv_arg == -2:
                    # every csv in separate list to create csv groups existing out of 1 csv file
                    print("\nre-listing")
                    print(csv_all_clean)
                    csv_message_list = [[x] for x in csv_all_clean]
                    print()
                    print(csv_message_list)
                    print("\n")

                # return specific file
                elif csv_arg >= -1:
                    user_input = None

                    if csv_arg >= 0:
                        user_input = csv_arg

                    # let user choose file if no file selected
                    while not isinstance(user_input, int) or not 0 <= user_input < no_files:
                        user_input = input("Please choose file you want to send as messages: ")
                        try:
                            user_input = int(user_input)

                            # if user number is outside numbered files
                            if not 0 <= user_input < no_files:
                                print("Input number does not match any listed file")

                        except ValueError:
                            print("Given input is not a number")

                    # single csv file in csv group
                    csv_message_list = [[csv_all_clean[user_input]]]

            else:
                print(f"No csv files found in folder {csv_folder_clean}")

        # return final list of csv files
        print(f"List of csv files for messaging: {csv_message_list}")
        return csv_message_list

    # return latest .csv
    def search_csv(self, csv_path, csv_arg="*", full_path=False):
        if csv_path.exists():
            # add .csv if filename is given without
            if csv_arg[-4:] != ".csv":
                csv_arg += ".csv"

            # find all files matching argument
            csv_path_list = csv_path.glob(csv_arg)

            csv_file_list = []
            for csv_file in csv_path_list:
                if full_path:
                    csv_file_list.append(csv_file)
                else:
                    csv_file_list.append(csv_file.name)

            return csv_file_list

        else:
            print(f"Folder '{csv_path}' not found.")
            return []


class OpenFaceMessage:
    def __init__(self):  # timestamp=b'', frame_no=b'', confidence=b'', pose=b'', gaze=b'', au_regression=b''
        self.msg = dict()

    def set_df(self, df_csv):
        self.df_csv = df_csv

    # get AU regression and head pose data as dataframe
    def df_split(self):
        #   split data frame
        # au_regression data frame
        au_regression_col = self.df_csv.columns.str.contains("AU.*_r")
        self.df_au = self.df_csv.loc[:, au_regression_col]
        # rename cols from AU**_r to AU**
        self.df_au.rename(columns=lambda x: x.replace('_r', ''), inplace=True)

        # head pose data frame
        head_pose_col = self.df_csv.columns.str.contains("pose_*")
        self.df_head_pose = self.df_csv.loc[:, head_pose_col]
        # rename cols from pose_* to pitch, roll, yaw
        # df_au_regression.rename({'pose_Rx': 'pitch', 'pose_Ry': 'roll', 'pose_Rz': 'yaw'},
        #                         axis='columns', inplace=True)

        # eye gaze data frame
        eye_gaze_col = self.df_csv.columns.str.contains("gaze_angle_*")
        self.df_eye_gaze = self.df_csv.loc[:, eye_gaze_col]

    def set_msg(self, frame_tracker):
        # get single frame
        row = self.df_csv.loc[frame_tracker]

        # init a message dict
        self.msg = dict()

        # get confidence in tracking if exist
        if 'confidence' in self.df_csv:
            self.msg['confidence'] = row['confidence']
        # if no confidence, set it to 1.0
        else:
            self.msg['confidence'] = 1.0

        # metadata in message
        self.msg['frame'] = int(row['frame'])
        self.msg['timestamp'] = row['timestamp']

        # check confidence high enough, else return None as data
        if self.msg['confidence'] >= .7:
            # au_regression in message
            self.msg['au_r'] = self.df_au.loc[frame_tracker].to_dict()
            # print(msg['au_r'])

            # eye gaze in message as AU
            eye_angle = self.df_eye_gaze.loc[frame_tracker].get(["gaze_angle_x", "gaze_angle_y"]).values  # radians
            print(eye_angle)
            # eyes go about 60 degree, which is 1.0472 rad, so no conversion needed?
            self.msg['gaze']['gaze_angle_x'] = eye_angle[0]
            self.msg['gaze']['gaze_angle_y'] = eye_angle[1]
            
            # set all to 0 (otherwise smoothing problems)
            #self.msg['au_r']['AU61'] = 0
            #self.msg['au_r']['AU62'] = 0
            #self.msg['au_r']['AU63'] = 0
            #self.msg['au_r']['AU64'] = 0

            # eye_angle_x left
            #if eye_angle[0] < 0:
            #    self.msg['au_r']['AU61'] = min(eye_angle[0]*-1, 1.0)
            # eye_angle_x right
            #else:
            #    self.msg['au_r']['AU62'] = min(eye_angle[0], 1.0)

            # eye_angle_y up
            #if eye_angle[1] >= 0:
            #    self.msg['au_r']['AU63'] = min(eye_angle[1], 1.0)
            # eye_angle_y down
            #else:
            #    self.msg['au_r']['AU64'] = min(eye_angle[1] * -1, 1.0)

            # head pose in message
            self.msg['pose'] = self.df_head_pose.loc[frame_tracker].to_dict()
            # print(msg['pose'])

    def set_reset_msg(self):
        # init a message dict
        self.msg = dict()

        # metadata in message
        self.msg['frame'] = -1
        self.msg['smooth'] = False  # don't smooth these data
        # self.msg['confidence'] = 2.0

        # au_regression in message
        au_r = {}
        # set all AUs to 0
        for i in range(29):
            au_r[f"AU{str(i).zfill(2)}"] = 0.0
        au_r["AU45"] = 0.0
        # AU03 does not exist
        au_r.pop("AU03")

        self.msg['au_r'] = au_r

        # head pose in message
        pose = {'pose_Rx': 0.0, 'pose_Ry': 0.0, 'pose_Rz': 0.0}
        self.msg['pose'] = pose


# generator for rows in FACS / head pose dataframe from FilterCSV
class OpenFaceMsgFromCSV:
    """
    Publishes FACS (Action Units) and head pos data from a cleaned OpenFace .csv

    """

    def __init__(self, csv_arg, csv_folder='openface', every_x_frames=1):  # client
        """
        generates messages from OpenFace .csv files

        :param csv_arg: csv_file_name, -2, -1, >=0
        :param csv_folder: where to look for csv files
        :param every_x_frames: send message when frame % every_x_frames == 0
        """

        self.crawler = CrawlerCSV()
        self.csv_list = self.crawler.gather_csv_list(csv_folder, csv_arg)
        print(f"using csv files: {self.csv_list}")
        self.reset_msg = OpenFaceMessage()
        self.reset_msg.set_reset_msg()
        self.every_x_frames = every_x_frames

    # loop over all csv groups ([1 csv file] if single person, P1, P2, etc [multi csv files]
    async def msg_gen(self):
        for csv_group in self.csv_list:
            print("\n\n")
            time_start = time.time()
            print(csv_group)
            # sys.exit("\nCSV crawler check finished")

            async for i, msg in self.msg_from_csv(csv_group):
                print(msg)
                timestamp = time.time()

                # return filename, timestamp and msg as JSON string
                yield f"p{i}." + csv_group[i].stem, timestamp - time_start, json.dumps(msg)

            # continue frame count
            # frame = msg['frame']
            # self.reset_msg.msg['frame'] = frame

            # send few empty messages when csv group is done
            await asyncio.sleep(1)
            for i in range(5):
                # self.reset_msg.msg['frame'] += i
                await asyncio.sleep(.05)
                yield "reset", timestamp - time_start, json.dumps(self.reset_msg.msg)
            await asyncio.sleep(.2)

        # return that messages are finished (Python >= 3.6)
        yield None

    # generator for FACS and head pose messages
    async def msg_from_csv(self, csv_group):
        """
        Generates messages from a csv file

        :param csv_group: list of path + file name(s) of csv file(s)
        :return: data of a message to be send in JSON
        """

        # if no csv in csv_group; range(0) == skip
        df_au_row_count = 0
        # dataframe per csv file
        ofmsg_list = []

        # load OpenFace csv as dataframe
        for csv in csv_group:
            # read csv as Pandas dataframe
            df_csv = pd.read_csv(csv)  # FilterCSV(csv).df_csv
            print(df_csv.head())

            # # check df same length when using multi-session
            # if df_au_row_count != 0:
            #     if not df_au_row_count == df_csv.shape[0]:
            #         sys.exit(f"rowcount of csv files not the same: {csv_group}")
            #
            # # if first dataframe, set number of rows
            # else:
            #     # get number of rows in dataframe;
            #     df_au_row_count = df_csv.shape[0]
            #     print("Data rows in data frame: {}".format(df_au_row_count))

            if df_csv.shape[0] > df_au_row_count:
                df_au_row_count = df_csv.shape[0]
                print("Data rows in data frame: {}".format(df_au_row_count))

            # create msg object with dataframe info
            ofmsg = OpenFaceMessage()
            ofmsg.set_df(df_csv)
            ofmsg.df_split()
            ofmsg_list.append(ofmsg)

        # get current time to match timestamp when publishing
        timer = time.time()

        # send all rows of data 1 by 1
        # message preparation before sleep, then return data
        for frame_tracker in range(df_au_row_count):
            print("FRAME TRACKER: {}".format(frame_tracker))

            # set message for every data frame
            for ofmsg in ofmsg_list:
                ofmsg.set_msg(frame_tracker)

            # get recorded timestamp from first user
            time_csv = ofmsg_list[0].msg['timestamp']

            # # Sleep before sending the messages, so processing time has less influence
            # wait until timer time matches timestamp
            time_sleep = time_csv - (time.time() - timer)
            print("waiting {} seconds before sending next message".format(time_sleep))

            # don't sleep negative time
            if time_sleep >= 0:
                # currently can send about 3000 fps
                await asyncio.sleep(time_sleep)  # time_sleep (~0.031)

            # reduce frame rate
            if frame_tracker % self.every_x_frames == 0:
                for i, ofmsg in enumerate(ofmsg_list):
                    # return msg dict
                    if 'au_r' in ofmsg.msg:
                        yield i, ofmsg.msg
                    # not enough confidence; return empty msg
                    else:
                        yield i, ''


class FACSvatarMessages(FACSvatarZeroMQ):
    """Publishes FACS and Head movement data from .csv files generated by OpenFace"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # init class to process .csv files
        self.openface_msg = OpenFaceMsgFromCSV(self.misc['csv_arg'], self.misc['csv_folder'],
                                               int(self.misc['every_x_frames']))

    # publishes facs values per frame to subscription key 'facs'
    async def facs_pub(self):
        """Calls openface_msg.msg_gen() and publishes returned data"""

        msg_count = 0

        # get FACS message
        async for msg in self.openface_msg.msg_gen():
            print(msg)
            # send message if we have data
            if msg:
                # reduce number of messages
                # if msg_count % 3 == 0:
                await self.pub_socket.send_multipart([(self.pub_key + "." + msg[0]).encode('ascii'),  # topic
                                                      str(int(time.time() * 1000)).encode('ascii'),  # timestamp
                                                      #int(msg[1]*1000).to_bytes(4, byteorder='big'),  # timestamp
                                                      msg[2].encode('utf-8')  # data in JSON format or empty byte
                                                      ])
                # else:
                #     print("Skipping message")

                msg_count += 1

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
    parser.add_argument("--pub_key", default="openface",
                        help="Key for filtering message; Default: openface")
    parser.add_argument("--pub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")
    parser.add_argument("--csv_arg", default="demo",
                        help="specific csv (allows for wildcard *), "
                             "-2: message all csv in specified folder, "
                             "-1: show csv list from specified folder, "
                             ">=0 choose specific csv file from list")
    parser.add_argument("--csv_folder", default="openface/default",
                        help="Name of folder with csv files; Default: openface")
    parser.add_argument("--every_x_frames", default="1",
                        help="Send every x frames a msg; Default 1 (all)")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))

    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.facs_pub])
