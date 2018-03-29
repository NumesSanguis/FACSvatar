//https://github.com/valkjsaaa/Unity-ZeroMQ-Example
using System.Collections.Concurrent;
using System.Threading;
using NetMQ;
using UnityEngine;
using NetMQ.Sockets;
using Newtonsoft.Json.Linq;

public class NetMqListener
{
    private readonly Thread _listenerWorker;
    private bool _listenerCancelled;
    public delegate void MessageDelegate(string message);
    private readonly MessageDelegate _messageDelegate;
    private readonly ConcurrentQueue<string> _messageQueue = new ConcurrentQueue<string>();
    private void ListenerWork()
    {
        Debug.Log("Setting up subscriber sock");
        AsyncIO.ForceDotNet.Force();
        using (var subSocket = new SubscriberSocket())
        {
            subSocket.Options.ReceiveHighWatermark = 1000;
            subSocket.Connect("tcp://localhost:5572");
            subSocket.Subscribe("");
            Debug.Log("sub socket initiliased");
            while (!_listenerCancelled)
            {
                string frameString;
                if (!subSocket.TryReceiveFrameString(out frameString)) continue;
                //Debug.Log(frameString);
                _messageQueue.Enqueue(frameString);
            }
            subSocket.Close();
        }
        NetMQConfig.Cleanup();
    }

    public void Update()
    {
        while (!_messageQueue.IsEmpty)
        {
            string message;
            if (_messageQueue.TryDequeue(out message))
            {
                _messageDelegate(message);
            }
            else
            {
                break;
            }
        }
    }

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

public class ZeroMQFACSvatar : MonoBehaviour
{
    private NetMqListener _netMqListener;

    // Facial expressions: Assign by dragging the GameObject with FACSnimator into the inspector before running the game.
    public FACSnimator FACSModel;
    // Head rotations: Assign by dragging the GameObject with HeadAnimator into the inspector before running the game.
    public HeadRotator RiggedModel;

    private void HandleMessage(string subMsg)
    {
        //Debug.Log(subMsg);
        JObject jsonMsg = JObject.Parse(subMsg);

        // get head pose data and send to main tread
        JObject head_pose = jsonMsg["data"]["head_pose"].ToObject<JObject>();
        UnityMainThreadDispatcher.Instance().Enqueue(RiggedModel.RequestHeadRotation(head_pose));

        // get Blend Shape dict
        JObject blend_shapes = jsonMsg["data"]["blend_shape"].ToObject<JObject>();
        UnityMainThreadDispatcher.Instance().Enqueue(FACSModel.RequestBlendshapes(blend_shapes));
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
