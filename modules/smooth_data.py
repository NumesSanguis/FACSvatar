import math
import asyncio
import pandas as pd
import sys
import copy
import json
from collections import defaultdict


class SmoothData:
    """stores received data to smooth data

    Input: data in json format
    Output: data in json format"""

    def __init__(self):
        # store dicts from previous time steps; e.g. [0] = facs, [1] = head_pose
        self.dataframe_list = []

    # smoothing function similar to softmax
    def softmax_smooth(self, series, steep=1):
        # series: 1 column as a pandas data series from a dataframe
        # steep: close to 0 means taking average, high steep means only looking at new data

        # print(f"Smoothing:\n{series}")

        # sum_0_n(e^(-steepness*n) x_n) / sum_0_n(e^(-steepness*n))
        numerator = 0
        denominator = 0
        for n, x in enumerate(series):  # reversed()
            numerator += math.exp(-steep * n) * x
            denominator += math.exp(-steep * n)  # TODO calculate once

        # print(f"numerator: {numerator}")
        # print(f"denominator: {denominator}")
        smooth = numerator / denominator
        # print(f"smooth: {smooth}\n")

        return smooth

    # use window of size 'window_size' data to smooth; window=1 is no smoothing
    def trailing_moving_average(self, data_dict, queue_no, window_size=3, steep=1):
        # data_dict: json formatted string containing data
        # queue_no: which data history should be used
        # trail: how many previous dicts should be remembered

        # no smoothing
        if window_size <= 1:
            return data_dict

        else:
            # convert dict to pandas dataframe
            # d_series = data_dict  # pd.read_json(data_dict, typ='series')

            # create a new queue to store a new type of data when no queue exist yet
            if len(self.dataframe_list) <= queue_no:
                # convert series to data frame
                # d_frame = d_series.to_frame()
                # use labels as column names; switch index with columns
                # d_frame = d_frame.transpose()

                print(data_dict)
                d_frame = pd.DataFrame.from_dict(data_dict, orient='index')
                d_frame = d_frame.transpose()
                # d_frame = pd.DataFrame.from_dict(list(data_dict.items()))
                print(d_frame)

                # add calculated denominator as meta-data
                # d_frame.steep = steep

                print("Add new queue")
                self.dataframe_list.append(d_frame)
                # return data frame in json format
                return data_dict

            # use [trail] previous data dicts for moving average
            else:
                # transform dict to series
                d_series = pd.Series(data_dict)

                # get data frame
                d_frame = self.dataframe_list[queue_no]

                # add data series to data frame at first postion
                # d_frame = d_frame.append(d_series, ignore_index=True)  # , ignore_index=True
                d_frame.loc[-1] = d_series  # adding a row
                d_frame.index = d_frame.index + 1  # shifting index
                d_frame = d_frame.sort_index()  # sorting by index

                # drop row when row count longer than trail
                if d_frame.shape[0] > window_size:
                    # drop first row (frame)
                    # d_frame.drop(d_frame.index[0], inplace=True)
                    # drop last row (oldest frame)
                    d_frame.drop(d_frame.tail(1).index, inplace=True)

                # put our data frame back for next time
                self.dataframe_list[queue_no] = d_frame

                # use softmax-like function to smooth
                smooth_data = d_frame.apply(self.softmax_smooth, args=(steep,))  # axis=1,

                return smooth_data.to_dict()
