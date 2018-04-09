import os
import sys
import argparse
import six
import time
import json
#import cv2
import glob

import asyncio
import zmq.asyncio
from zmq.asyncio import Context

# own imports
from openfacefiltercsv import FilterCSV

# # global sleep to match video with publisher
# global_publish_time = 0.033
# global_start_video = False


# # process everything that is received
# class SubscribeProcessor:
#     def __init__(self, log):
#         self.log = log
#
#     def message_handler(self, counter, id, type):
#         print('----------------------------')
#         self.log.info("'oncounter' event, counter value: {counter}", counter=counter)
#         self.log.info("from component {id} ({type})", id=id, type=type)


# TODO use yield to return message
# publish what this node contributes
class FACSMsgFromCSV:
    def __init__(self,):  # client
        self.filter_csv = FilterCSV

    # generator for FACS messages
    async def facs_msg_gen(self, file='head_test.csv'):
        # # global sleep for showing video
        # global global_publish_time
        # global global_start_video

        # self.log.info("Starting publishing")
        # load OpenFace csv as dataframe
        self.df_au = FilterCSV(file).df_au
        print(self.df_au.head())

        # get number of rows in dataframe
        df_au_row_count = self.df_au.shape[0]
        print(df_au_row_count)
        print(type(df_au_row_count))

        # sleep to match video output
        #await asyncio.sleep(0.5)

        # get current time to match timestamp when publishing
        timer = time.time()

        # allow video to be played
        #global_start_video = True

        # send all rows of data 1 by 1
        # Calculations before sleep, then publish
        for frame_tracker in range(df_au_row_count):
            print("FRAME TRACKER: {}".format(frame_tracker))

            # get AU/other values of 1 frame and transform it to a dict
            # TODO pandas to_json
            # https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
            # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.to_json.html
            msg_dict = self.structure_dict(self.df_au.iloc[frame_tracker])

            # show json contents
            #print(json.dumps(msg_dict, indent=4))

            # # Sleep before sending the messages, so processing time has less influence
            # wait until timer time matches timestamp
            time_sleep = msg_dict['timestamp'] - (time.time() - timer)
            print("waiting {} seconds before sending next FACS".format(time_sleep))

            # set time new frame should be shown
            #global_publish_time = time.time() + time_sleep + 0.0025

            # don't sleep negative time
            if time_sleep >= 0:
                # currently can send about 3000 fps
                await asyncio.sleep(time_sleep)  # time_sleep (~0.031)

            # Blender rendering slow down
            # await asyncio.sleep(.2)

            # only publish message if we have data
            if msg_dict['data']:
                # publish FACS + gaze to topic; convert to JSON
                # yield in async gen (Python >= 3.6)
                yield json.dumps(msg_dict)
            else:
                print("Tracking confidence too low; not publishing message")
                # self.log.info("Tracking confidence too low; not publishing message")

        # return that messages are finished (Python >= 3.6)
        yield None

    # async def publishing(self, msg):
    #     # cast datarow into JSON format
    #     #print(type(datarow.to_json()))
    #
    #     # json.dumps(msg).encode()
    #     self.publish('eu.surafusoft.facs', msg)  # .to_json() # , self._ident, self._type

    # restructure json message to frame, timestamp, data={head_pose, AU} (send None if confidence <0.6)
    def structure_dict(self, datarow):
        msg_dict = datarow.to_dict()

        # restructure
        msg_dict_re = {}
        msg_dict_re['frame'] = msg_dict['frame']
        msg_dict_re['timestamp'] = msg_dict['timestamp']

        # add data if enough confidence in tracking
        if msg_dict['confidence'] >= 0.6:
            # TODO split FACS and gaze (when data aggregation problem is solved)

            msg_dict_re['data'] = {}  # 'head_pose': {}, 'FACS': {}
            # msg_dict.startswith(query)  # .items()
            # copy dict elements when key starts with 'pose_R'
            msg_dict_re['data']['head_pose'] = {k: v for k, v in msg_dict.items() if k.startswith('pose_R')}
            # copy dict elements when key starts with 'pose_R'; assumes we only have AU**_r
            msg_dict_re['data']['facs'] = {k: v for k, v in msg_dict.items() if k.startswith('AU')}

        # confidence too low --> return None
        else:
            msg_dict_re['data'] = None

        return msg_dict_re


# # TODO put video in subscriber node to make it independent; use 1 time function to set right video
# # play Open Face recorded video in sync with avatar
# class ViewVideo:
#     def __init__(self, fn):
#         # fn: file name of video
#
#         self.fn = fn
#         # stop frame reading when buffer is full
#         #self.stopped = False
#
#         loop = asyncio.get_event_loop()
#         # no need for run_until_complete(), because event loop doesn't have to be started twice
#         asyncio.ensure_future(self.open_video(loop))
#
#     async def open_video(self, loop):
#         # loop: asyncio asynchronous event tracker
#
#         vid = cv2.VideoCapture(self.fn)
#         # Check if camera opened successfully
#         if not vid.isOpened():
#             print("Error opening video stream or file")
#         else:
#             # create new asyncio event loop and pass to new thread
#             new_loop = asyncio.new_event_loop()
#             # open new thread to play video to not block the main thread
#             await loop.run_in_executor(None, self.play_video, new_loop, vid)  # new_loop,
#
#         # if something has to be returned from new thread:
#         # https://stackoverflow.com/questions/32059732/send-asyncio-tasks-to-loop-running-in-other-thread
#
#     # new thread; producer / consumer for buffering / showing video
#     def play_video(self, loop, vid):
#         # get frame rate
#         fps = vid.get(cv2.CAP_PROP_FPS)
#         print("Playing Open Face video with fps: {}".format(fps))
#
#         # give time for publisher to get ready
#         #time.sleep(.11)
#
#         print("\nnew loop: {}\n".format(loop))
#         # set new event loop
#         asyncio.set_event_loop(loop)
#         # get new set event loop
#         thread_loop = asyncio.get_event_loop()  # loop
#
#         print("set loop: {}\n".format(thread_loop))
#
#         # set video frame queue
#         queue = asyncio.Queue(maxsize=120, loop=thread_loop)
#         frame_enqueue_coro = self.frame_enqueue(queue, vid)
#         frame_show_coro = self.frame_show(queue, fps)
#         print(frame_enqueue_coro)
#         print(frame_show_coro)
#         thread_loop.run_until_complete(asyncio.gather(frame_enqueue_coro, frame_show_coro))
#         thread_loop.close()
#
#     # puts video frames into a queue
#     async def frame_enqueue(self, queue, vid):
#         while vid.isOpened():
#             ret, frame = vid.read()
#
#             # if we still have frames
#             if ret:
#                 # due to maxsize of queue, it should wait with putting in new automatically
#                 await queue.put(frame)
#                 #await asyncio.sleep(0.01)
#             else:
#                 await queue.put(None)
#                 vid.release()
#
#     # display frames from queue
#     async def frame_show(self, queue, fps):
#         while True:
#             # wait until FACS publisher is ready
#             if global_start_video:
#                 frame = await queue.get()
#                 #print("frame: {}".format(frame))
#                 # display frames as long as we don't receive None
#                 if frame is not None:
#                     if cv2.waitKey(1) & 0xFF == ord('q'):
#                         break
#                     cv2.imshow('frame', frame)
#                     # await asyncio.sleep((1/fps)-0.0062)
#                     # await asyncio.sleep(global_sleep-0.01)
#                     time_sleep = global_publish_time - time.time()
#                     if time_sleep >= 0:
#                         await asyncio.sleep(time_sleep)
#                 else:
#                     cv2.destroyAllWindows()
#                     break
#
#             # wait a bit before checking if publisher is ready
#             else:
#                 await asyncio.sleep(0.02)


# goes through 'openface' folder to find latest .csv
class CrawlerCSV:
    # return latest .csv
    def search(self, folder='openface'):
        csv_list = sorted(glob.glob(os.path.join(folder, '*.csv')))

        # # get latest .csv
        # 2nd or higher run
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
    Our WAMP session class .. setup register/subscriber/publisher here
    """
    def __init__(self, address='127.0.0.1', port='5570'):
        self.url = "tcp://{}:{}".format(address, port)
        self.ctx = Context.instance()

        self.facs_csv = FACSMsgFromCSV()

        # activate publishers / subscribers
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.facs_pub(),
        ]))

    # publishes facs values per frame to topic 'facs'
    async def facs_pub(self, topic='human01'):
        pub = self.ctx.socket(zmq.PUB)
        pub.connect(self.url)
        print("FACS pub initialized")

        # ask if we use demo video or new recorded one
        # if input("Use demo video? y/n: ").lower() == "y":
        #     file = "Takimoto_demo"
        # else:
        #file = CrawlerCSV().search()

        # play Open Face video matching .csv file
        #ViewVideo(file+'.avi')

        # read csv and publish FACS
        #await self.publish_processor.start_pub(file+'.csv')

        # get FACS message
        async for msg in self.facs_csv.facs_msg_gen():
            print(msg)
            # send message if we have data
            if msg:
                # TODO seperate data from meta-data
                await pub.send_multipart([topic.encode('ascii'), msg.encode('utf-8')])

            # done
            else:
                print("FACS done")

    # def onLeave(self, details):
    #     self.log.info("Router session closed ({details})", details=details)
    #     self.disconnect()

    # def onDisconnect(self):
    #     self.log.info("Router connection closed")
    #     try:
    #         asyncio.get_event_loop().stop()
    #     except:
    #         pass


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
