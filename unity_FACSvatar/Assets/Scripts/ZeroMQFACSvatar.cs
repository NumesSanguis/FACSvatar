//https://github.com/valkjsaaa/Unity-ZeroMQ-Example
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Threading;
using NetMQ;
using UnityEngine;
using NetMQ.Sockets;
using Newtonsoft.Json.Linq;

// connect with ZeroMQ
public class NetMqListener
{
    private readonly Thread _listenerWorker;
    private bool _listenerCancelled;
    public delegate void MessageDelegate(List<string> msg_list);
    private readonly MessageDelegate _messageDelegate;
    private readonly ConcurrentQueue<List<string>> _messageQueue = new ConcurrentQueue<List<string>>();
    private void ListenerWork()
    {
        Debug.Log("Setting up subscriber sock");
        AsyncIO.ForceDotNet.Force();
        using (var subSocket = new SubscriberSocket())
        {
            // set limit on how many messages in memory
            subSocket.Options.ReceiveHighWatermark = 1000;
            // socket connection
            subSocket.Connect("tcp://localhost:5572");
            // subscribe to topics; "" == all topics
            subSocket.Subscribe("");
            Debug.Log("sub socket initiliased");

            string topic;
            string frame;
            string timestamp;
            string blend_shapes;
            string head_pose;
            while (!_listenerCancelled)
            {
                //string frameString;
                // wait for full message
                //if (!subSocket.TryReceiveFrameString(out frameString)) continue;
                //Debug.Log(frameString);
                //_messageQueue.Enqueue(frameString);

                List<string> msg_list = new List<string>();
                if (!subSocket.TryReceiveFrameString(out topic)) continue;
                if (!subSocket.TryReceiveFrameString(out frame)) continue;
                if (!subSocket.TryReceiveFrameString(out timestamp)) continue;
                if (!subSocket.TryReceiveFrameString(out blend_shapes)) continue;
                if (!subSocket.TryReceiveFrameString(out head_pose)) continue;

                //Debug.Log("Received messages:");
                //Debug.Log(frame);
                //Debug.Log(timestamp);
                //Debug.Log(blend_shapes);
                //Debug.Log(head_pose);

                // check if we're not done
                if (frame != "")
                {
                    msg_list.Add(blend_shapes);
                    msg_list.Add(head_pose);
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

    // Facial expressions: Assign by dragging the GameObject with FACSnimator into the inspector before running the game.
    public FACSnimator FACSModel;
    // Head rotations: Assign by dragging the GameObject with HeadAnimator into the inspector before running the game.
    public HeadRotator RiggedModel;

    // receive data in JSON format
    private void HandleMessage(List<string> msg_list)
    {
        JObject blend_shapes = JObject.Parse(msg_list[0]);
        JObject head_pose = JObject.Parse(msg_list[1]);

        // get Blend Shape dict
        UnityMainThreadDispatcher.Instance().Enqueue(FACSModel.RequestBlendshapes(blend_shapes));

        // get head pose data and send to main tread
        UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel.RequestHeadRotation(head_pose));
    }

    private void Start()
    {
        _netMqListener = new NetMqListener(HandleMessage);
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
