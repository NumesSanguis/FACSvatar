import asyncio
import pandas as pd
import copy
import json
from collections import defaultdict


class SmoothData:
    """stores received data to smooth data

    Input: data in json format
    Output: data in json format"""

    def __init__(self):
        # store dicts from previous time steps; e.g. [0] = facs, [1] = head_pose
        self.queue_list = []

    async def trailing_moving_average(self, data_json, queue_no, trail=2, alpha=1):
        # data_json: json formatted string containing data
        # queue_no: which data history should be used
        # trail: how many previous dicts should be remembered

        print("Smoothing FACS / head_pose data with past data...")

        # convert json to pandas dataframe
        d_series = pd.read_json(data_json, typ='series')
        print(d_series)
        # print(d_series.type())

        # create a new queue to store a new type of data
        if len(self.queue_list) <= queue_no:
            # convert series to data frame
            d_frame = d_series.to_frame()
            print(d_frame)

            print("Add new queue")
            self.queue_list.append([d_frame])
            # return data frame in json format
            return d_series.to_json()

        # # don't smooth if queue is not full
        # elif len(self.queue_list[queue_no]) < trail:
        #     print("Queue not full yet")
        #     self.queue_list[queue_no].append(data_dict)
        #     # return unchanged data
        #     return data_dict

        # use [trail] previous data dicts for moving average
        else:
            print("\n\n")
            print(d_series)

            # get data frame
            d_frame = self.queue_list[queue_no]

            # add data series to data frame


            # add unmodified dict to queue (position 3, not use for smoothing
            # .append(json.loads(json.dumps(data_dict))); thread safe deep copy
            self.queue_list[queue_no].append(data_dict)
            print("len queue list: {}".format(len(self.queue_list[queue_no])))
            print(self.queue_list[queue_no][0])
            print(self.queue_list[queue_no][1])
            print(self.queue_list[queue_no][2])


            # weighted smooth with previous dict
            # https://stackoverflow.com/a/35689816/3399066
            # TODO different trail length than 3
            data_dict = {e: data_dict[e] * .7 +
                            self.queue_list[queue_no][0][e] * .2 +
                            self.queue_list[queue_no][1][e] * .1
                         for e in data_dict}

            # remove oldest dict
            print("\n\nPopping: {}".format(self.queue_list[queue_no].pop(0)))

            print("")
            print(data_dict)
            print(self.queue_list[queue_no][0])
            print(self.queue_list[queue_no][1])
            return data_dict

    async def trailing_moving_average_old(self, data_dict, queue_no, trail=2):
        # data_dict: dict containing data
        # queue_no: which data history should be used
        # trail: how many previous dicts should be remembered

        print("Smoothing FACS data with trailing average...")

        # store a new queue for new type of data
        if len(self.queue_list) <= queue_no:
            print("Add new queue")
            self.queue_list.append([data_dict])
            return data_dict

        # don't smooth if queue is not full
        elif len(self.queue_list[queue_no]) < trail:
            print("Queue not full yet")
            self.queue_list[queue_no].append(data_dict)
            # return unchanged data
            return data_dict

        # use [trail] previous data dicts for moving average
        else:
            print("\n\n")
            print(data_dict)

            # add unmodified dict to queue (position 3, not use for smoothing
            # .append(json.loads(json.dumps(data_dict))); thread safe deep copy
            self.queue_list[queue_no].append(data_dict)
            print("len queue list: {}".format(len(self.queue_list[queue_no])))
            print(self.queue_list[queue_no][0])
            print(self.queue_list[queue_no][1])
            print(self.queue_list[queue_no][2])


            # weighted smooth with previous dict
            # https://stackoverflow.com/a/35689816/3399066
            # TODO different trail length than 3
            data_dict = {e: data_dict[e] * .7 +
                            self.queue_list[queue_no][0][e] * .2 +
                            self.queue_list[queue_no][1][e] * .1
                         for e in data_dict}

            # remove oldest dict
            print("\n\nPopping: {}".format(self.queue_list[queue_no].pop(0)))

            print("")
            print(data_dict)
            print(self.queue_list[queue_no][0])
            print(self.queue_list[queue_no][1])
            return data_dict
