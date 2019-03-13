# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import sys
import os
import argparse
from pathlib import Path
import shutil
from os.path import join
import json
import csv


# own imports; if statement for documentation
if __name__ == '__main__':
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ


class MessageToFile:
    def __init__(self, folder_output):
        self.folder_output = Path(folder_output)
        # self.removefilesinfolder(self.folder_output)
        self.movefilestoback(self.folder_output)
        self.msg_key = None  # check if new file is being processed

    # move old files to bak
    def movefilestoback(self, folder_path):
        import shutil

        folder_bak = folder_path.parent / (folder_path.name + "_bak")

        # check bak folder exist
        print("Check folder exist")
        if folder_bak.exists():
            shutil.rmtree(folder_bak)

        # rename existing folder to *_bak
        if folder_path.exists():
            folder_path.rename(folder_bak)

        folder_path.mkdir(exist_ok=True)

    # # delete old files; currently not used
    # def removefilesinfolder(self, folder_path):
    #     for file in os.listdir(folder_path):
    #         file_path = Path(folder_path, file)
    #         try:
    #             file_path.unlink()
    #             # elif os.path.isdir(file_path): shutil.rmtree(file_path)
    #         except Exception as e:
    #             print(e)

    def data_json(self, key, data):
        # save data as JSON

        # reset if new file being processed
        if key != self.msg_key:
            self.msg_key = key
            # create new folder for new processed data
            (self.folder_output / self.msg_key).mkdir(exist_ok=True)

        print(json.dumps(data, indent=4))
        # save FACS data to JSON
        with open(Path(self.folder_output, self.msg_key, "frame_{}.json".format(data["frame"])), 'w') as outfile:
            json.dump(data, outfile)

    def data_csv(self, key, data):
        # save data as CSV

        # # reset when processing new folder
        # if key != self.msg_key:
        #     self.msg_key = key

        # see if au_r exist in data
        try:
            aublend_dict = data.pop("au_r")
        # otherwise use blendshape values
        except KeyError:
            aublend_dict = data.pop("blendshapes")
        pose_dict = data.pop("pose")
        # remove utc timestamp
        _ = data.pop("timestamp_utc", "")
        # flatten dict
        dict_flat = {**data, **pose_dict, **aublend_dict}
        print(dict_flat)

        with open(Path(self.folder_output, "{}.csv".format(key)), 'a') as outfile:
            writer = csv.DictWriter(outfile, dict_flat.keys(), delimiter=',')
            if data["frame"] == 0:
                writer.writeheader()
            writer.writerow(dict_flat)
        #     writer = csv.writer(outfile, delimiter=',')
        #     if self.counter == 0:
        #         writer.writeheader()
        #     writer.writerow()


    def stop(self):
        print("All messages received")


# client to message broker server
class FACSvatarMessages(FACSvatarZeroMQ):
    """Receives FACS and Head movement data; forward to output function"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_to_file = MessageToFile(self.misc['folder_output'])

    async def sub(self):
        # keep listening to all published message on topic 'facs'
        while True:
            key, timestamp, data = await self.sub_socket.sub()
            print("Received message: {}".format([key, timestamp, data]))

            # check not finished; timestamp is empty (b'')
            if timestamp:
                # process facs data only
                if self.misc['file_format'] == "json":
                    self.message_to_file.data_json(key, data)  # data['au_r']
                elif self.misc['file_format'] == "csv":
                    self.message_to_file.data_csv(key, data)

            # no more messages to be received
            else:
                print("No more messages to publish")
                self.message_to_json.stop()


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()

    # subscriber to FACS / head movement data
    parser.add_argument("--sub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--sub_port", default="5571",
                        help="Port of where to pub to; Default: 5571")
    parser.add_argument("--sub_key", default=argparse.SUPPRESS,
                        help="Key for filtering message; Default: '' (all keys)")
    parser.add_argument("--sub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")

    # module specific commandline arguments
    parser.add_argument("--file_format", default="json",
                        help="specific file format of how to store data;"
                             "json, csv; Default: json")
    parser.add_argument("--folder_output", default="data_output",
                        help="Path to folder for saving data")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))
    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.sub])
