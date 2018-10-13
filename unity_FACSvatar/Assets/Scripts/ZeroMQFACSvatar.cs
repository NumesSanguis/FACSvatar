//https://github.com/valkjsaaa/Unity-ZeroMQ-Example
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Threading;
using NetMQ;
using UnityEngine;
using NetMQ.Sockets;
using Newtonsoft.Json.Linq;
using System;
using System.IO;

public enum Participants
{
    users_1_models_1, users_1_models_2, users_1_models_2_dnn,
    users_2_models_2, users_2_models_2_dnn, users_2_models_3_dnn
}

// connect with ZeroMQ
public class NetMqListener
{
    public string sub_to_ip;
    public string sub_to_port;
    public bool facsvatar_logging = false;
    private readonly Thread _listenerWorker;
    private bool _listenerCancelled;
    public delegate void MessageDelegate(List<string> msg_list);
    private readonly MessageDelegate _messageDelegate;
    private readonly ConcurrentQueue<List<string>> _messageQueue = new ConcurrentQueue<List<string>>();
    //private string csv_folder = "Assets/Logging/";
	  private string csv_path = "Assets/Logging/unity_timestamps_sub.csv";
	  private StreamWriter csv_writer;
	  private long msg_count;
    public NetMqListener(string sub_to_ip, string sub_to_port) {
        this.sub_to_ip = sub_to_ip;
        this.sub_to_port = sub_to_port;
    }

    private void ListenerWork()
    {
		    Debug.Log("Setting up subscriber sock");
        AsyncIO.ForceDotNet.Force();
        using (var subSocket = new SubscriberSocket())
        {
            // set limit on how many messages in memory
            subSocket.Options.ReceiveHighWatermark = 1000;
            // socket connection
            // subSocket.Connect("tcp://localhost:5572");
            subSocket.Connect("tcp://"+sub_to_ip+":"+sub_to_port);
            // subscribe to topics; "" == all topics
            subSocket.Subscribe("");
            Debug.Log("sub socket initiliased");

            string topic;
            //string frame;
            string timestamp;
            //string blend_shapes;
            //string head_pose;
            string facsvatar_json;
            while (!_listenerCancelled)
            {
                //string frameString;
                // wait for full message
                //if (!subSocket.TryReceiveFrameString(out frameString)) continue;
                //Debug.Log(frameString);
                //_messageQueue.Enqueue(frameString);

                List<string> msg_list = new List<string>();
                if (!subSocket.TryReceiveFrameString(out topic)) continue;
                //if (!subSocket.TryReceiveFrameString(out frame)) continue;
                if (!subSocket.TryReceiveFrameString(out timestamp)) continue;
                //if (!subSocket.TryReceiveFrameString(out blend_shapes)) continue;
                //if (!subSocket.TryReceiveFrameString(out head_pose)) continue;
                if (!subSocket.TryReceiveFrameString(out facsvatar_json)) continue;

                //Debug.Log("Received messages:");
                //Debug.Log(frame);
                //Debug.Log(timestamp);
				        //Debug.Log(facsvatar_json);

                // check if we're not done; timestamp is empty
                if (timestamp != "")
                {
                    msg_list.Add(topic);
					          msg_list.Add(timestamp);
                    msg_list.Add(facsvatar_json);
                    long timeNowMs = UnixTimeNowMillisec();
                    msg_list.Add(timeNowMs.ToString());  // time msg received; for unity performance
                    
                    if (facsvatar_logging == true)
                    {
					              //Debug.Log("NetMqListener log");
					              
					              //Debug.Log(timeNowMs);
					              //Debug.Log(timestamp2);
					              //Debug.Log(timeNowMs - timestamp2);

					              // write to csv
					              // string csvLine = string.Format("{0},{1},{2}", msg_count, timestamp2, timeNowMs);
					              string csvLine = string.Format("{0},{1}", msg_count, timeNowMs);
					              csv_writer.WriteLine(csvLine);
					          }
					          msg_count++;
					          
                    _messageQueue.Enqueue(msg_list);
                }
                // done
                else
                {
                    Debug.Log("Received all messages");
                }
            }
            subSocket.Close();
        }
        NetMQConfig.Cleanup();
    }

	public static long UnixTimeNowMillisec()
    {
        DateTime unixStart = new DateTime(1970, 1, 1, 0, 0, 0, 0, System.DateTimeKind.Utc);
        long unixTimeStampInTicks = (DateTime.UtcNow - unixStart).Ticks;
		    long timeNowMs = unixTimeStampInTicks / (TimeSpan.TicksPerMillisecond / 10000);  // 100ns
        //Debug.Log(timeNowMs);
        return timeNowMs;
    }

    // check queue for messages
    public void Update()
    {
        while (!_messageQueue.IsEmpty)
        {
            List<string> msg_list;
            if (_messageQueue.TryDequeue(out msg_list))
            {
                _messageDelegate(msg_list);
            }
            else
            {
                break;
            }
        }
    }

    // threaded message listener
    public NetMqListener(MessageDelegate messageDelegate)
    {
        _messageDelegate = messageDelegate;
        _listenerWorker = new Thread(ListenerWork);
    }

    public void Start()
    {
        if (facsvatar_logging == true)
        {
		        // logging
		        Debug.Log("Setting up Logging NetMqListener");
		        msg_count = -1;
		        File.Delete(csv_path);  // delete previous csv if exist
		        csv_writer = new StreamWriter(csv_path, true);  // , true
            csv_writer.WriteLine("msg,time_prev,time_now");
		        csv_writer.Flush();
            //csv_writer.Close();
		        //csv_writer.Open();
		        //csv_writer.WriteLine("time_prev,time_now");
		        //csv_writer.Close();
        }

        _listenerCancelled = false;
        _listenerWorker.Start();
    }

    public void Stop()
    {
        _listenerCancelled = true;
        _listenerWorker.Join();
        if (facsvatar_logging == true)
        {
		        csv_writer.Close();
		    }
    }
}

// act on messages received
public class ZeroMQFACSvatar : MonoBehaviour
{
    private NetMqListener _netMqListener;
    public string sub_to_ip = "127.0.0.1";
    public string sub_to_port = "5572";
    public bool facsvatar_logging = false;

    public Participants participants;

    // logging
	  private long msg_count;
	  private string csv_folder = "Assets/Logging/";
	  private string csv_path = "Assets/Logging/unity_timestamps_sub.csv";
	  private StreamWriter csv_writer;   
	  private string csv_path_total = "Assets/Logging/unity_timestamps_total.csv";
    private StreamWriter csv_writer_total;


    // Facial expressions: Assign by dragging the GameObject with FACSnimator into the inspector before running the game.
    // Head rotations: Assign by dragging the GameObject with HeadAnimator into the inspector before running the game.
    public FACSnimator FACSModel0;
	  public HeadRotatorBone RiggedModel0;
	  public FACSnimator FACSModel1;
	  public HeadRotatorBone RiggedModel1;
    public FACSnimator FACSModelDnn;
	  public HeadRotatorBone RiggedModelDnn;

    // 2 users 2 models dnn case ignore data from replaced participant
    private string userIgnoreString = "p1";

    // receive data in JSON format
    private void HandleMessage(List<string> msg_list)
    {
        JObject facsvatar = JObject.Parse(msg_list[2]);
        // get Blend Shape dict
        JObject blend_shapes = facsvatar["blendshapes"].ToObject<JObject>();
		    // get head pose data
		    JObject head_pose = facsvatar["pose"].ToObject<JObject>();
            
		    // split topic to determine target human model
		    //Debug.Log(msg_list[0]);
		    string[] topic_info = msg_list[0].Split('.'); // "facsvatar.S01_P1.p0.dnn" ["facsvatar", "S01_P1", "p0", "dnn"]


        // send to main tread
        // 1 person
        //Debug.Log(participants);
        //Debug.Log(participants.GetType());

        // ignore dnn data
        if (participants == Participants.users_1_models_1 & Array.IndexOf(topic_info, "dnn") == -1)
        {
            UnityMainThreadDispatcher.Instance().Enqueue(FACSModel0.RequestBlendshapes(blend_shapes));
            UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel0.RequestHeadRotation(head_pose));
        }

        // ignore dnn data
        else if (participants == Participants.users_1_models_2 & Array.IndexOf(topic_info, "dnn") == -1)
        {
            UnityMainThreadDispatcher.Instance().Enqueue(FACSModel0.RequestBlendshapes(blend_shapes));
            UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel0.RequestHeadRotation(head_pose));
            UnityMainThreadDispatcher.Instance().Enqueue(FACSModel1.RequestBlendshapes(blend_shapes));
            UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel1.RequestHeadRotation(head_pose));
        }

        else if (participants == Participants.users_1_models_2_dnn)
        {
            if (Array.IndexOf(topic_info, "dnn") != -1)
            {
                UnityMainThreadDispatcher.Instance().Enqueue(FACSModelDnn.RequestBlendshapes(blend_shapes));
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModelDnn.RequestHeadRotation(head_pose));
            }
            else
            {
                UnityMainThreadDispatcher.Instance().Enqueue(FACSModel0.RequestBlendshapes(blend_shapes));
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel0.RequestHeadRotation(head_pose));
            }
        }

        // ignore dnn data
        else if (participants == Participants.users_2_models_2 & Array.IndexOf(topic_info, "dnn") == -1)
        {
            if (Array.IndexOf(topic_info, "p0") != -1)
            {
                UnityMainThreadDispatcher.Instance().Enqueue(FACSModel0.RequestBlendshapes(blend_shapes));
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel0.RequestHeadRotation(head_pose));
            }
            else if (Array.IndexOf(topic_info, "p1") != -1)
            {
                UnityMainThreadDispatcher.Instance().Enqueue(FACSModel1.RequestBlendshapes(blend_shapes));
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel1.RequestHeadRotation(head_pose));
            }
        }

        else if (participants == Participants.users_2_models_2_dnn)
        {
            // only use AU data from DNN, not head movement

            if (Array.IndexOf(topic_info, "dnn") != -1)
            {
                userIgnoreString = facsvatar["user_ignore"].ToString();

                //if (Array.IndexOf(topic_info, "p0") != -1)
                if (userIgnoreString == "p0")
                {
                    UnityMainThreadDispatcher.Instance().Enqueue(FACSModel0.RequestBlendshapes(blend_shapes));
                    //UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel0.RequestHeadRotation(head_pose));
                }
                //else if (Array.IndexOf(topic_info, "p1") != -1)
                else if (userIgnoreString == "p1")
                {
                    UnityMainThreadDispatcher.Instance().Enqueue(FACSModel1.RequestBlendshapes(blend_shapes));
                    //UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel1.RequestHeadRotation(head_pose));
                }
            }

            else if (Array.IndexOf(topic_info, "p0") != -1)
            {
                // only use AU data when not provided by DNN
                if (userIgnoreString != "p0")
                {
                    UnityMainThreadDispatcher.Instance().Enqueue(FACSModel0.RequestBlendshapes(blend_shapes));
                }
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel0.RequestHeadRotation(head_pose));
            }

            else if (Array.IndexOf(topic_info, "p1") != -1)
            {
                // only use AU data when not provided by DNN
                if (userIgnoreString != "p1")
                {
                    UnityMainThreadDispatcher.Instance().Enqueue(FACSModel1.RequestBlendshapes(blend_shapes));
                }
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel1.RequestHeadRotation(head_pose));
            }
        }

        else if (participants == Participants.users_2_models_3_dnn)
        {
            if (Array.IndexOf(topic_info, "dnn") != -1)
            {
                UnityMainThreadDispatcher.Instance().Enqueue(FACSModelDnn.RequestBlendshapes(blend_shapes));
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModelDnn.RequestHeadRotation(head_pose));
            }
            else if (Array.IndexOf(topic_info, "p0") != -1)
            {
                UnityMainThreadDispatcher.Instance().Enqueue(FACSModel0.RequestBlendshapes(blend_shapes));
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel0.RequestHeadRotation(head_pose));
            }
            else if (Array.IndexOf(topic_info, "p1") != -1)
            {
                UnityMainThreadDispatcher.Instance().Enqueue(FACSModel1.RequestBlendshapes(blend_shapes));
                UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel1.RequestHeadRotation(head_pose));
            }
        }

    if (facsvatar_logging == true)
    {
		    // logging
		    //Debug.Log("ZeroMQFACSvatar log");
		    long timeNowMs = UnixTimeNowMillisec();
		    long timestampMsgArrived = Convert.ToInt64(msg_list[3]);
        //Debug.Log(timeNowMs);
		    //Debug.Log(timestampMsgArrived);
		    //Debug.Log(timeNowMs - timestampMsgArrived);

        // write to csv
		    string csvLine = string.Format("{0},{1},{2}", msg_count, timestampMsgArrived, timeNowMs);
        csv_writer.WriteLine(csvLine);

		    // if data contains timestamp_utc, write total time      
		    if (facsvatar["timestamp_utc"] != null)
		    {
			    //Debug.Log(facsvatar["timestamp_utc"]);
			    long timeFirstSend = Convert.ToInt64(facsvatar["timestamp_utc"].ToString());
			    //Debug.Log((timeNowMs - timeFirstSend) / 10000);

			    // write to csv
			    string csvLine_total = string.Format("{0},{1},{2}", msg_count, timeFirstSend, timeNowMs);
          csv_writer_total.WriteLine(csvLine_total);
		    }
		}

		msg_count++;
    }

	public static long UnixTimeNowMillisec()
    {
        DateTime unixStart = new DateTime(1970, 1, 1, 0, 0, 0, 0, System.DateTimeKind.Utc);
        long unixTimeStampInTicks = (DateTime.UtcNow - unixStart).Ticks;
        long timeNowMs = unixTimeStampInTicks / (TimeSpan.TicksPerMillisecond / 10000);  // 100ns
        //Debug.Log(timeNowMs);
        return timeNowMs;
    }

    private void Start()
    {
        if (facsvatar_logging == true)
        {
		        // logging
		        Debug.Log("Setting up Logging ZeroMQFACSvatar");
            msg_count = -1;

            Directory.CreateDirectory(csv_folder);
            File.Delete(csv_path);  // delete previous csv if exist
            csv_writer = new StreamWriter(csv_path, true);  // true; keep steam open
            csv_writer.WriteLine("msg,time_prev,time_now");
            csv_writer.Flush();

		        File.Delete(csv_path_total);  // delete previous csv if exist
		        csv_writer_total = new StreamWriter(csv_path_total, true);  // true; keep steam open
		        csv_writer_total.WriteLine("msg,time_prev,time_now");
		        csv_writer_total.Flush();
		    }

        _netMqListener = new NetMqListener(HandleMessage);
        _netMqListener.sub_to_ip = sub_to_ip;
        _netMqListener.sub_to_port = sub_to_port;
        _netMqListener.Start();
    }

    private void Update()
    {
        _netMqListener.Update();
    }

    private void OnDestroy()
    {
        _netMqListener.Stop();
    }
}
