//https://github.com/valkjsaaa/Unity-ZeroMQ-Example
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Threading;
using NetMQ;
using UnityEngine;
using NetMQ.Sockets;
using Newtonsoft.Json.Linq;
using System;

// connect with ZeroMQ
public class NetMqListener
{
    public string sub_to_ip;
    public string sub_to_port;
    private readonly Thread _listenerWorker;
    private bool _listenerCancelled;
    public delegate void MessageDelegate(List<string> msg_list);
    private readonly MessageDelegate _messageDelegate;
    private readonly ConcurrentQueue<List<string>> _messageQueue = new ConcurrentQueue<List<string>>();
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
        _listenerCancelled = false;
        _listenerWorker.Start();
    }

    public void Stop()
    {
        _listenerCancelled = true;
        _listenerWorker.Join();
    }
}

// act on messages received
public class ZeroMQFACSvatar : MonoBehaviour
{
    private NetMqListener _netMqListener;
    public string sub_to_ip = "127.0.0.1";
    public string sub_to_port = "5572";

	// Facial expressions: Assign by dragging the GameObject with FACSnimator into the inspector before running the game.
	// Head rotations: Assign by dragging the GameObject with HeadAnimator into the inspector before running the game.
	public FACSnimator FACSModel0;
	public HeadRotatorBone RiggedModel0;
	public FACSnimator FACSModel1;
	public HeadRotatorBone RiggedModel1;
    public FACSnimator FACSModelDnn;
	public HeadRotatorBone RiggedModelDnn;

    // receive data in JSON format
    private void HandleMessage(List<string> msg_list)
    {
        JObject facsvatar = JObject.Parse(msg_list[2]);
        // get Blend Shape dict
        JObject blend_shapes = facsvatar["blendshapes"].ToObject<JObject>();
		// get head pose data
		JObject head_pose = facsvatar["pose"].ToObject<JObject>();
        
		// split topic to determine target human model
		string[] topic_info = msg_list[0].Split('.'); // "facsvatar.S01_P1.p0.dnn" ["facsvatar", "S01_P1", "p0", "dnn"]
        
		// send to main tread
		// TODO should be possible without code duplication
	    if (Array.IndexOf(topic_info, "dnn") != -1)
		{
			UnityMainThreadDispatcher.Instance().Enqueue(FACSModel1.RequestBlendshapes(blend_shapes));
			UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel1.RequestHeadRotation(head_pose));
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

    private void Start()
    {
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
