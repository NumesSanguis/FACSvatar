///////////////////////////////////////////////////////////////////////////////
// Copyright (C) 2017, Carnegie Mellon University and University of Cambridge,
// all rights reserved.
//
// ACADEMIC OR NON-PROFIT ORGANIZATION NONCOMMERCIAL RESEARCH USE ONLY
//
// BY USING OR DOWNLOADING THE SOFTWARE, YOU ARE AGREEING TO THE TERMS OF THIS LICENSE AGREEMENT.  
// IF YOU DO NOT AGREE WITH THESE TERMS, YOU MAY NOT USE OR DOWNLOAD THE SOFTWARE.
//
// License can be found in OpenFace-license.txt

//     * Any publications arising from the use of this software, including but
//       not limited to academic journal and conference publications, technical
//       reports and manuals, must cite at least one of the following works:
//
//       OpenFace 2.0: Facial Behavior Analysis Toolkit
//       Tadas Baltrušaitis, Amir Zadeh, Yao Chong Lim, and Louis-Philippe Morency
//       in IEEE International Conference on Automatic Face and Gesture Recognition, 2018  
//
//       Convolutional experts constrained local model for facial landmark detection.
//       A. Zadeh, T. Baltrušaitis, and Louis-Philippe Morency,
//       in Computer Vision and Pattern Recognition Workshops, 2017.    
//
//       Rendering of Eyes for Eye-Shape Registration and Gaze Estimation
//       Erroll Wood, Tadas Baltrušaitis, Xucong Zhang, Yusuke Sugano, Peter Robinson, and Andreas Bulling 
//       in IEEE International. Conference on Computer Vision (ICCV),  2015 
//
//       Cross-dataset learning and person-specific normalisation for automatic Action Unit detection
//       Tadas Baltrušaitis, Marwa Mahmoud, and Peter Robinson 
//       in Facial Expression Recognition and Analysis Challenge, 
//       IEEE International Conference on Automatic Face and Gesture Recognition, 2015 
//
///////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////
// This file is modified by Hung-Hsuan Huang for ZeroMQ integration.
// His homepage: http://hhhuang.homelinux.com
// If there are any comments or questions, please send to hhhuang@acm.org
// To compile this file, the developer need to install the following two packages
// NetMQ and Newtonsoft.Json
// They can be download from the nuget portal site
///////////////////////////////////////////////////////////////////////////////

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using System.Windows;
using System.Windows.Threading;
using System.Windows.Media.Imaging;
using System.Windows.Controls;
using Microsoft.WindowsAPICodePack.Dialogs;

// Internal libraries
using OpenCVWrappers;
using CppInterop.LandmarkDetector;
using FaceAnalyser_Interop;
using GazeAnalyser_Interop;
using FaceDetectorInterop;
using UtilitiesOF;

// By Huang
using NetMQ;
using NetMQ.Sockets;
using Newtonsoft.Json;
using System.Net;
using System.IO;
using System.Xml;

namespace OpenFaceOffline
{
    // Added by Huang
    public struct JsonData
    {
        public double timestamp;
        public long frame;
        public double confidence;
        public struct Pose
        {
            public double pose_Tx;
            public double pose_Ty;
            public double pose_Tz;
            public double pose_Rx;
            public double pose_Ry;
            public double pose_Rz;
        }
        public Pose pose;
        public struct Gaze
        {
            public double gaze_angle_x;
            public double gaze_angle_y;
            public double gaze_0_x;
            public double gaze_0_y;
            public double gaze_0_z;
            public double gaze_1_x;
            public double gaze_1_y;
            public double gaze_1_z;
        }
        public Gaze gaze;
        public Dictionary<string, double> au_c;
        public Dictionary<string, double> au_r;
    }
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        // By Huang
        PublisherSocket pubSocket = null;
        long frame_no = 0;
        string topic = "openface";
        //Mode running_mode = Mode.standalone;                           

        // Timing for measuring FPS
        #region High-Resolution Timing
        static DateTime startTime;
        static Stopwatch sw = new Stopwatch();

        static MainWindow()
        {
            startTime = DateTime.Now;
            sw.Start();
        }

        public static DateTime CurrentTime
        {
            get { return startTime + sw.Elapsed; }
        }
        #endregion

        // -----------------------------------------------------------------
        // Members
        // -----------------------------------------------------------------

        Thread processing_thread;

        // Some members for displaying the results
        private WriteableBitmap latest_img;
        private WriteableBitmap latest_aligned_face;
        private WriteableBitmap latest_HOG_descriptor;

        // Managing the running of the analysis system
        private volatile bool thread_running;
        private volatile bool thread_paused = false;
        // Allows for going forward in time step by step
        // Useful for visualising things
        private volatile int skip_frames = 0;

        FpsTracker processing_fps = new FpsTracker();

        // For selecting webcams
        CameraSelection cam_sec;

        // For tracking
        FaceDetector face_detector;
        FaceModelParameters face_model_params;
        CLNF landmark_detector;

        // For face analysis
        FaceAnalyserManaged face_analyser;
        GazeAnalyserManaged gaze_analyser;

        public bool RecordAligned { get; set; } = false; // Aligned face images
        public bool RecordHOG { get; set; } = false; // HOG features extracted from face images
        public bool Record2DLandmarks { get; set; } = true; // 2D locations of facial landmarks (in pixels)
        public bool Record3DLandmarks { get; set; } = true; // 3D locations of facial landmarks (in pixels)
        public bool RecordModelParameters { get; set; } = true; // Facial shape parameters (rigid and non-rigid geometry)
        public bool RecordPose { get; set; } = true; // Head pose (position and orientation)
        public bool RecordAUs { get; set; } = true; // Facial action units
        public bool RecordGaze { get; set; } = true; // Eye gaze
        public bool RecordTracked { get; set; } = true; // Recording tracked videos or images

        // Visualisation options
        public bool ShowTrackedVideo { get; set; } = true; // Showing the actual tracking
        public bool ShowAppearance { get; set; } = true; // Showing appeaance features like HOG
        public bool ShowGeometry { get; set; } = true; // Showing geometry features, pose, gaze, and non-rigid
        public bool ShowAUs { get; set; } = true; // Showing Facial Action Units

        int image_output_size = 112;
        public bool MaskAligned { get; set; } = true; // Should the aligned images be masked

        // Where the recording is done (by default in a record directory, from where the application executed)
        String record_root = "./processed";

        // Selecting which face detector will be used
        public bool DetectorHaar { get; set; } = false;
        public bool DetectorHOG { get; set; } = false;
        public bool DetectorCNN { get; set; } = true;

        // Selecting which landmark detector will be used
        public bool LandmarkDetectorCLM { get; set; } = false;
        public bool LandmarkDetectorCLNF { get; set; } = false;
        public bool LandmarkDetectorCECLM { get; set; } = true;

        // For AU prediction, if videos are long dynamic models should be used
        public bool DynamicAUModels { get; set; } = true;

        // Camera calibration parameters
        public float fx = -1, fy = -1, cx = -1, cy = -1;

        public MainWindow()
        {
            // added by Huang
            bool bPush = false;

            string configfile_name = "config.xml";

            FileStream stream = new FileStream(configfile_name, FileMode.Open);
            XmlDocument document = new XmlDocument();
            document.Load(stream);

            string serveraddress = "localhost";
            int port = 5570;


            XmlNodeList list = document.GetElementsByTagName("Mode");
            if (list.Count > 0 && ((XmlElement)list[0]).InnerText.ToLower().Equals("push"))
                bPush = true;
            list = document.GetElementsByTagName("IP");
            if (list.Count > 0)
            {
                serveraddress = ((XmlElement)list[0]).InnerText;
            }
            list = document.GetElementsByTagName("Port");
            if (list.Count > 0)
            {
                port = Int32.Parse(((XmlElement)list[0]).InnerText);
            }
            list = document.GetElementsByTagName("Topic");
            if (list.Count > 0)
            {
                topic = ((XmlElement)list[0]).InnerText;
            }


            String hostName = Dns.GetHostName();
            IPAddress[] addresses = Dns.GetHostAddresses(hostName);

            string myaddress = "localhost";


            foreach (IPAddress address in addresses)
            {
                if (address.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                {
                    myaddress = address.ToString();
                }
            }

            // End of Huang's code
            InitializeComponent();
            this.DataContext = this; // For WPF data binding

            // Set the icon
            Uri iconUri = new Uri("logo1.ico", UriKind.RelativeOrAbsolute);
            this.Icon = BitmapFrame.Create(iconUri);

            String root = AppDomain.CurrentDomain.BaseDirectory;
                        
            face_model_params = new FaceModelParameters(root, LandmarkDetectorCECLM, LandmarkDetectorCLNF, LandmarkDetectorCLM);
            // Initialize the face detector
            face_detector = new FaceDetector(face_model_params.GetHaarLocation(), face_model_params.GetMTCNNLocation());

            // If MTCNN model not available, use HOG
            if (!face_detector.IsMTCNNLoaded())
            {
                FaceDetCNN.IsEnabled = false;
                DetectorCNN = false;
                DetectorHOG = true;
            }
            face_model_params.SetFaceDetector(DetectorHaar, DetectorHOG, DetectorCNN);

            landmark_detector = new CLNF(face_model_params);

            gaze_analyser = new GazeAnalyserManaged();

            // Added by Huang
            frame_no = 0;
            pubSocket = new PublisherSocket();
            pubSocket.Options.SendHighWatermark = 1000;
            if (bPush)
                pubSocket.Connect("tcp://" + serveraddress + ":" + port);
            else
                pubSocket.Bind("tcp://" + myaddress + ":" + port);
            // end of Huang's code                        
        }

        // ----------------------------------------------------------
        // Actual work gets done here

        // Wrapper for processing multiple sequences
        private void ProcessSequences(List<String> filenames)
        {
            for (int i = 0; i < filenames.Count; ++i)
            {
                SequenceReader reader = new SequenceReader(filenames[i], false, fx, fy, cx, cy);
                ProcessSequence(reader);

                // Before continuing to next video make sure the user did not stop the processing
                if (!thread_running)
                {
                    break;
                }
            }

        }

        // The main function call for processing sequences
        private void ProcessSequence(SequenceReader reader)
        {
            Thread.CurrentThread.Priority = ThreadPriority.Highest;

            SetupFeatureExtractionMode();

            thread_running = true;

            // Reload the face landmark detector if needed
            ReloadLandmarkDetector();

            if(!landmark_detector.isLoaded())
            {
                DetectorNotFoundWarning();
                EndMode();
                thread_running = false;
                return;
            }

            // Set the face detector
            face_model_params.SetFaceDetector(DetectorHaar, DetectorHOG, DetectorCNN);
            face_model_params.optimiseForVideo();

            // Setup the visualization
            Visualizer visualizer_of = new Visualizer(ShowTrackedVideo || RecordTracked, ShowAppearance, ShowAppearance, false);

            // Initialize the face analyser
            face_analyser = new FaceAnalyserManaged(AppDomain.CurrentDomain.BaseDirectory, DynamicAUModels, image_output_size, MaskAligned);

            // Reset the tracker
            landmark_detector.Reset();

            // Loading an image file
            var frame = reader.GetNextImage();
            var gray_frame = reader.GetCurrentFrameGray();

            // Setup recording
            RecorderOpenFaceParameters rec_params = new RecorderOpenFaceParameters(true, reader.IsWebcam(),
                Record2DLandmarks, Record3DLandmarks, RecordModelParameters, RecordPose, RecordAUs,
                RecordGaze, RecordHOG, RecordTracked, RecordAligned, false,
                reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy(), reader.GetFPS());

            RecorderOpenFace recorder = new RecorderOpenFace(reader.GetName(), rec_params, record_root);

            // For FPS tracking
            DateTime? startTime = CurrentTime;
            var lastFrameTime = CurrentTime;

            // Empty image would indicate that the stream is over
            while (!gray_frame.IsEmpty)
            {

                if(!thread_running)
                {
                    break;
                }

                double progress = reader.GetProgress();
                
                bool detection_succeeding = landmark_detector.DetectLandmarksInVideo(frame, face_model_params, gray_frame);

                // The face analysis step (for AUs and eye gaze)
                face_analyser.AddNextFrame(frame, landmark_detector.CalculateAllLandmarks(), detection_succeeding, false);

                gaze_analyser.AddNextFrame(landmark_detector, detection_succeeding, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy());

                // Only the final face will contain the details
                VisualizeFeatures(frame, visualizer_of, landmark_detector.CalculateAllLandmarks(), landmark_detector.GetVisibilities(), detection_succeeding, true, false, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy(), progress);

                // Record an observation
                RecordObservation(recorder, visualizer_of.GetVisImage(), 0, detection_succeeding, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy(), reader.GetTimestamp(), reader.GetFrameNumber());

                // this line is added by Huang
                SendZeroMQMessage(detection_succeeding, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy(), reader.GetTimestamp());


                if(RecordTracked)
                { 
                    recorder.WriteObservationTracked();
                }

                while (thread_running & thread_paused && skip_frames == 0)
                {
                    Thread.Sleep(10);
                }

                if (skip_frames > 0)
                    skip_frames--;

                frame = reader.GetNextImage();
                gray_frame = reader.GetCurrentFrameGray();

                lastFrameTime = CurrentTime;
                processing_fps.AddFrame();
            }

            // Finalize the recording and flush to disk
            recorder.Close();

            // Post-process the AU recordings
            if(RecordAUs)
            { 
                face_analyser.PostProcessOutputFile(recorder.GetCSVFile());
            }

            // Close the open video/webcam
            reader.Close();

            EndMode();

        }

        private void ProcessIndividualImages(ImageReader reader)
        {
            // Make sure the GUI is setup appropriately
            SetupFeatureExtractionMode();

            // Indicate we will start running the thread
            thread_running = true;

            // Reload the face landmark detector if needed
            ReloadLandmarkDetector();

            if (!landmark_detector.isLoaded())
            {
                DetectorNotFoundWarning();
                EndMode();
                thread_running = false;
                return;
            }

            // Setup the parameters optimized for working on individual images rather than sequences
            face_model_params.optimiseForImages();

            // Setup the visualization
            Visualizer visualizer_of = new Visualizer(ShowTrackedVideo || RecordTracked, ShowAppearance, ShowAppearance, false);

            // Initialize the face detector if it has not been initialized yet
            if (face_detector == null)
            {
                face_detector = new FaceDetector(face_model_params.GetHaarLocation(), face_model_params.GetMTCNNLocation());
            }

            // Initialize the face analyser
            face_analyser = new FaceAnalyserManaged(AppDomain.CurrentDomain.BaseDirectory, false, image_output_size, MaskAligned);

            // Loading an image file
            var frame = reader.GetNextImage();
            var gray_frame = reader.GetCurrentFrameGray();

            // For FPS tracking
            DateTime? startTime = CurrentTime;
            var lastFrameTime = CurrentTime;

            // This will be false when the image is not available
            while (reader.isOpened())
            {
                if (!thread_running)
                {
                    break;
                }

                // Setup recording
                RecorderOpenFaceParameters rec_params = new RecorderOpenFaceParameters(false, false,
                    Record2DLandmarks, Record3DLandmarks, RecordModelParameters, RecordPose, RecordAUs,
                    RecordGaze, RecordHOG, RecordTracked, RecordAligned, true,
                    reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy(), 0);

                RecorderOpenFace recorder = new RecorderOpenFace(reader.GetName(), rec_params, record_root);

                visualizer_of.SetImage(frame, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy());

                // Detect faces here and return bounding boxes
                List<Rect> face_detections = new List<Rect>();
                List<float> confidences = new List<float>();
                if(DetectorHOG)
                {
                    face_detector.DetectFacesHOG(face_detections, gray_frame, confidences);
                }
                else if(DetectorCNN)
                { 
                    face_detector.DetectFacesMTCNN(face_detections, frame, confidences);
                }
                else if(DetectorHaar)
                {
                    face_detector.DetectFacesHaar(face_detections, gray_frame, confidences);
                }

                // For visualization
                double progress = reader.GetProgress();

                for (int i = 0; i < face_detections.Count; ++i)
                {
                    bool detection_succeeding = landmark_detector.DetectFaceLandmarksInImage(frame, face_detections[i], face_model_params, gray_frame);

                    var landmarks = landmark_detector.CalculateAllLandmarks();
                    
                    // Predict action units
                    var au_preds = face_analyser.PredictStaticAUsAndComputeFeatures(frame, landmarks);

                    // Predic eye gaze
                    gaze_analyser.AddNextFrame(landmark_detector, detection_succeeding, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy());

                    // Only the final face will contain the details
                    VisualizeFeatures(frame, visualizer_of, landmarks, landmark_detector.GetVisibilities(), detection_succeeding, i == 0, true, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy(), progress);

                    // Record an observation
                    RecordObservation(recorder, visualizer_of.GetVisImage(), i, detection_succeeding, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy(), 0, 0);

                    // This line is added by Huang
                    SendZeroMQMessage(detection_succeeding, reader.GetFx(), reader.GetFy(), reader.GetCx(), reader.GetCy(), 0);                   
                }

                recorder.SetObservationVisualization(visualizer_of.GetVisImage());

                frame = reader.GetNextImage();
                gray_frame = reader.GetCurrentFrameGray();

                // Write out the tracked image
                if(RecordTracked)
                { 
                    recorder.WriteObservationTracked();
                }

                // Do not cary state accross images
                landmark_detector.Reset();
                face_analyser.Reset();
                recorder.Close();

                lastFrameTime = CurrentTime;
                processing_fps.AddFrame();
                
                // TODO how to report errors from the reader here? exceptions? logging? Problem for future versions?
            }

            EndMode();

        }

        // If the landmark detector model changed need to reload it
        private void ReloadLandmarkDetector()
        {
            bool reload = false;
            if (face_model_params.IsCECLM() && !LandmarkDetectorCECLM)
            {
                reload = true;
            }
            else if(face_model_params.IsCLNF() && !LandmarkDetectorCLNF)
            {
                reload = true;
            }
            else if (face_model_params.IsCLM() && !LandmarkDetectorCLM)
            {
                reload = true;
            }

            if(reload)
            {
                String root = AppDomain.CurrentDomain.BaseDirectory;

                face_model_params = new FaceModelParameters(root, LandmarkDetectorCECLM, LandmarkDetectorCLNF, LandmarkDetectorCLM);
                landmark_detector = new CLNF(face_model_params);
            }
        }

        private void DetectorNotFoundWarning()
        {
            string messageBoxText = "Could not open the landmark detector model file. For instructions of how to download them, see https://github.com/TadasBaltrusaitis/OpenFace/wiki/Model-download";
            string caption = "Model file not found or corrupt";
            MessageBoxButton button = MessageBoxButton.OK;
            MessageBoxImage icon = MessageBoxImage.Warning;

            // Display message box
            System.Windows.MessageBox.Show(messageBoxText, caption, button, icon);

        }

        private void RecordObservation(RecorderOpenFace recorder, RawImage vis_image, int face_id, bool success, float fx, float fy, float cx, float cy, double timestamp, int frame_number)
        {

            recorder.SetObservationTimestamp(timestamp);

            double confidence = landmark_detector.GetConfidence();

            List<float> pose = new List<float>();
            landmark_detector.GetPose(pose, fx, fy, cx, cy);
            recorder.SetObservationPose(pose);

            List<Tuple<float, float>> landmarks_2D = landmark_detector.CalculateAllLandmarks();
            List<Tuple<float, float, float>> landmarks_3D = landmark_detector.Calculate3DLandmarks(fx, fy, cx, cy);
            List<float> global_params = landmark_detector.GetRigidParams();
            List<float> local_params = landmark_detector.GetNonRigidParams();

            recorder.SetObservationLandmarks(landmarks_2D, landmarks_3D, global_params, local_params, confidence, success);

            var gaze = gaze_analyser.GetGazeCamera();
            var gaze_angle = gaze_analyser.GetGazeAngle();

            var landmarks_2d_eyes = landmark_detector.CalculateAllEyeLandmarks();
            var landmarks_3d_eyes = landmark_detector.CalculateAllEyeLandmarks3D(fx, fy, cx, cy);
            recorder.SetObservationGaze(gaze.Item1, gaze.Item2, gaze_angle, landmarks_2d_eyes, landmarks_3d_eyes);

            var au_regs = face_analyser.GetCurrentAUsReg();
            var au_classes = face_analyser.GetCurrentAUsClass();
            recorder.SetObservationActionUnits(au_regs, au_classes);

            recorder.SetObservationFaceID(face_id);
            recorder.SetObservationFrameNumber(frame_number);

            recorder.SetObservationFaceAlign(face_analyser.GetLatestAlignedFace());
            
            var hog_feature = face_analyser.GetLatestHOGFeature();
            recorder.SetObservationHOG(success, hog_feature, face_analyser.GetHOGRows(), face_analyser.GetHOGCols(), face_analyser.GetHOGChannels());

            recorder.SetObservationVisualization(vis_image);

            recorder.WriteObservation();


        }

        // added by Stef
        public static long UnixTimeNowMillisec()
        {
            DateTime unixStart = new DateTime(1970, 1, 1, 0, 0, 0, 0, System.DateTimeKind.Utc);
            long unixTimeStampInTicks = (DateTime.UtcNow - unixStart).Ticks;
            long timeNowMs = unixTimeStampInTicks / (TimeSpan.TicksPerMillisecond / 10000);  // 100ns
                                                                                             //Debug.Log(timeNowMs);
            return timeNowMs;
        }

        // added by Huang
        private void SendZeroMQMessage(bool success, float fx, float fy, float cx, float cy, double openface_timestamp)
        {
            Tuple<float, float> gaze_angle = new Tuple<float, float>(0, 0);
            List<float> pose = new List<float>();
            List<float> non_rigid_params = landmark_detector.GetNonRigidParams();



            NetMQMessage output_message = new NetMQMessage();
            output_message.Append(topic);

            JsonData json_data = new JsonData();

            json_data.frame = frame_no++;

            //DateTime origin = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc);
            //TimeSpan difference = DateTime.UtcNow - origin;
            //output_message.Append((long)difference.TotalMilliseconds);
            output_message.Append((UnixTimeNowMillisec()).ToString());  // Changed by Stef

            json_data.timestamp = openface_timestamp;

            double confidence = landmark_detector.GetConfidence();
            if (confidence < 0)
                confidence = 0;
            else if (confidence > 1)
                confidence = 1;
            json_data.confidence = confidence;

            pose = new List<float>();
            landmark_detector.GetPose(pose, fx, fy, cx, cy);

            json_data.pose.pose_Tx = pose[0];
            json_data.pose.pose_Ty = pose[1];
            json_data.pose.pose_Tz = pose[2];
            json_data.pose.pose_Rx = pose[3];
            json_data.pose.pose_Ry = pose[4];
            json_data.pose.pose_Rz = pose[5];

            gaze_angle = gaze_analyser.GetGazeAngle();
            var gaze = gaze_analyser.GetGazeCamera();

            json_data.gaze.gaze_angle_x = gaze_angle.Item1;
            json_data.gaze.gaze_angle_y = gaze_angle.Item2;
            json_data.gaze.gaze_0_x = gaze.Item1.Item1;
            json_data.gaze.gaze_0_y = gaze.Item1.Item2;
            json_data.gaze.gaze_0_z = gaze.Item1.Item3;
            json_data.gaze.gaze_1_x = gaze.Item2.Item1;
            json_data.gaze.gaze_1_y = gaze.Item2.Item2;
            json_data.gaze.gaze_1_z = gaze.Item2.Item3;

            json_data.au_c = face_analyser.GetCurrentAUsClass();

            Dictionary<string, double> au_regs = face_analyser.GetCurrentAUsReg();
            json_data.au_r = new Dictionary<string, double>();
            foreach (KeyValuePair<string, double> au_reg in au_regs)
            {
                json_data.au_r[au_reg.Key] = au_reg.Value / 5.0;
                if (json_data.au_r[au_reg.Key] < 0)
                    json_data.au_r[au_reg.Key] = 0;

                if (json_data.au_r[au_reg.Key] > 1)
                    json_data.au_r[au_reg.Key] = 1;
            }

            string json_string = JsonConvert.SerializeObject(json_data);
            output_message.Append(json_string);
            pubSocket.SendMultipartMessage(output_message);

        }
        private void VisualizeFeatures(RawImage frame, Visualizer visualizer, List<Tuple<float, float>> landmarks, List<bool> visibilities, bool detection_succeeding, 
            bool new_image, bool multi_face, float fx, float fy, float cx, float cy, double progress)
        {

            List<Tuple<Point, Point>> lines = null;
            List<Tuple<float, float>> eye_landmarks = null;
            List<Tuple<Point, Point>> gaze_lines = null;
            Tuple<float, float> gaze_angle = new Tuple<float, float>(0, 0);

            List<float> pose = new List<float>();
            landmark_detector.GetPose(pose, fx, fy, cx, cy);
            List<float> non_rigid_params = landmark_detector.GetNonRigidParams();

            double confidence = landmark_detector.GetConfidence();

            if (confidence < 0)
                confidence = 0;
            else if (confidence > 1)
                confidence = 1;

            double scale = landmark_detector.GetRigidParams()[0];

            // Helps with recording and showing the visualizations
            if (new_image)
            {
                visualizer.SetImage(frame, fx, fy, cx, cy);
            }
            visualizer.SetObservationHOG(face_analyser.GetLatestHOGFeature(), face_analyser.GetHOGRows(), face_analyser.GetHOGCols());
            visualizer.SetObservationLandmarks(landmarks, confidence, visibilities);
            visualizer.SetObservationPose(pose, confidence);
            visualizer.SetObservationGaze(gaze_analyser.GetGazeCamera().Item1, gaze_analyser.GetGazeCamera().Item2, landmark_detector.CalculateAllEyeLandmarks(), landmark_detector.CalculateAllEyeLandmarks3D(fx, fy, cx, cy), confidence);

            eye_landmarks = landmark_detector.CalculateVisibleEyeLandmarks();
            lines = landmark_detector.CalculateBox(fx, fy, cx, cy);

            gaze_lines = gaze_analyser.CalculateGazeLines(fx, fy, cx, cy);
            gaze_angle = gaze_analyser.GetGazeAngle();

            // Visualisation (as a separate function)
            Dispatcher.Invoke(DispatcherPriority.Render, new TimeSpan(0, 0, 0, 0, 200), (Action)(() =>
            {
                if (ShowAUs)
                {
                    var au_classes = face_analyser.GetCurrentAUsClass();
                    var au_regs = face_analyser.GetCurrentAUsReg();

                    auClassGraph.Update(au_classes);

                    var au_regs_scaled = new Dictionary<String, double>();
                    foreach (var au_reg in au_regs)
                    {
                        au_regs_scaled[au_reg.Key] = au_reg.Value / 5.0;
                        if (au_regs_scaled[au_reg.Key] < 0)
                            au_regs_scaled[au_reg.Key] = 0;

                        if (au_regs_scaled[au_reg.Key] > 1)
                            au_regs_scaled[au_reg.Key] = 1;
                    }
                    auRegGraph.Update(au_regs_scaled);
                }

                if (ShowGeometry)
                {
                    int yaw = (int)(pose[4] * 180 / Math.PI + 0.5);
                    int roll = (int)(pose[5] * 180 / Math.PI + 0.5);
                    int pitch = (int)(pose[3] * 180 / Math.PI + 0.5);

                    YawLabel.Content = yaw + "°";
                    RollLabel.Content = roll + "°";
                    PitchLabel.Content = pitch + "°";

                    XPoseLabel.Content = (int)pose[0] + " mm";
                    YPoseLabel.Content = (int)pose[1] + " mm";
                    ZPoseLabel.Content = (int)pose[2] + " mm";

                    nonRigidGraph.Update(non_rigid_params);

                    // Update eye gaze
                    String x_angle = String.Format("{0:F0}°", gaze_angle.Item1 * (180.0 / Math.PI));
                    String y_angle = String.Format("{0:F0}°", gaze_angle.Item2 * (180.0 / Math.PI));
                    GazeXLabel.Content = x_angle;
                    GazeYLabel.Content = y_angle;
                }

                if (ShowTrackedVideo)
                {
                    if (new_image)
                    {
                        latest_img = frame.CreateWriteableBitmap();
                        overlay_image.Clear();
                    }

                    frame.UpdateWriteableBitmap(latest_img);

                    // Clear results from previous image
                    overlay_image.Source = latest_img;
                    overlay_image.Confidence.Add(confidence);
                    overlay_image.FPS = processing_fps.GetFPS();
                    overlay_image.Progress = progress;
                    overlay_image.FaceScale.Add(scale);

                    // Update results even if it is not succeeding when in multi-face mode
                    if(detection_succeeding || multi_face)
                    {

                        List<Point> landmark_points = new List<Point>();
                        foreach (var p in landmarks)
                        {
                            landmark_points.Add(new Point(p.Item1, p.Item2));
                        }

                        List<Point> eye_landmark_points = new List<Point>();
                        foreach (var p in eye_landmarks)
                        {
                            eye_landmark_points.Add(new Point(p.Item1, p.Item2));
                        }

                        overlay_image.OverlayLines.Add(lines);
                        overlay_image.OverlayPoints.Add(landmark_points);
                        overlay_image.OverlayPointsVisibility.Add(visibilities);
                        overlay_image.OverlayEyePoints.Add(eye_landmark_points);
                        overlay_image.GazeLines.Add(gaze_lines);
                    }
                }

                if (ShowAppearance)
                {
                    RawImage aligned_face = face_analyser.GetLatestAlignedFace();
                    RawImage hog_face = visualizer.GetHOGVis();

                    if (latest_aligned_face == null)
                    {
                        latest_aligned_face = aligned_face.CreateWriteableBitmap();
                        latest_HOG_descriptor = hog_face.CreateWriteableBitmap();
                    }

                    aligned_face.UpdateWriteableBitmap(latest_aligned_face);
                    hog_face.UpdateWriteableBitmap(latest_HOG_descriptor);

                    AlignedFace.Source = latest_aligned_face;
                    AlignedHOG.Source = latest_HOG_descriptor;
                }
            }));


        }

        private void StopTracking()
        {
            // First complete the running of the thread
            if (processing_thread != null)
            {
                // Tell the other thread to finish
                thread_running = false;
                processing_thread.Join();
            }
        }


        // ----------------------------------------------------------
        // Mode handling (image, video)
        // ----------------------------------------------------------

        // Disable GUI components that should not be active during processing
        private void SetupFeatureExtractionMode()
        {
            Dispatcher.Invoke((Action)(() =>
            {
                SettingsMenu.IsEnabled = false;
                RecordingMenu.IsEnabled = false;
                AUSetting.IsEnabled = false;
                FaceDetectorMenu.IsEnabled = false;
                LandmarkDetectorMenu.IsEnabled = false;

                PauseButton.IsEnabled = true;
                StopButton.IsEnabled = true;
                NextFiveFramesButton.IsEnabled = false;
                NextFrameButton.IsEnabled = false;
            }));
        }

        // When the processing is done re-enable the components
        private void EndMode()
        {
            latest_img = null;
            skip_frames = 0;

            // Unpause if it's paused
            if (thread_paused)
            {
                Dispatcher.Invoke(DispatcherPriority.Render, new TimeSpan(0, 0, 0, 0, 200), (Action)(() =>
                {
                    PauseButton_Click(null, null);
                }));
            }

            Dispatcher.Invoke(DispatcherPriority.Render, new TimeSpan(0, 0, 0, 1, 0), (Action)(() =>
            {

                SettingsMenu.IsEnabled = true;
                RecordingMenu.IsEnabled = true;
                AUSetting.IsEnabled = true;
                FaceDetectorMenu.IsEnabled = true;
                LandmarkDetectorMenu.IsEnabled = true;

                PauseButton.IsEnabled = false;
                StopButton.IsEnabled = false;
                NextFiveFramesButton.IsEnabled = false;
                NextFrameButton.IsEnabled = false;

                // Clean up the interface itself
                overlay_image.Source = null;
                
                auClassGraph.Update(new Dictionary<string, double>());
                auRegGraph.Update(new Dictionary<string, double>());
                YawLabel.Content = "0°";
                RollLabel.Content = "0°";
                PitchLabel.Content = "0°";

                XPoseLabel.Content = "0 mm";
                YPoseLabel.Content = "0 mm";
                ZPoseLabel.Content = "0 mm";

                nonRigidGraph.Update(new List<float>());

                GazeXLabel.Content = "0°";
                GazeYLabel.Content = "0°";
                
                AlignedFace.Source = null;
                AlignedHOG.Source = null;

            }));
        }

        // ----------------------------------------------------------
        // Opening Videos/Images
        // ----------------------------------------------------------

        // Some utilities for opening images/videos and directories
        private List<string> openMediaDialog(bool images)
        {
            string[] image_files = new string[0];
            Dispatcher.Invoke(DispatcherPriority.Render, new TimeSpan(0, 0, 0, 2, 0), (Action)(() =>
            {
                var d = new Microsoft.Win32.OpenFileDialog();
                d.Multiselect = true;
                if (images)
                {
                    d.Filter = "Image files|*.jpg;*.jpeg;*.bmp;*.png;*.gif";
                }
                else
                {
                    d.Filter = "Video files|*.avi;*.webm;*.wmv;*.mov;*.mpg;*.mpeg;*.mp4";
                }
                if (d.ShowDialog(this) == true)
                {

                    image_files = d.FileNames;

                }
            }));
            List<string> img_files_list = new List<string>(image_files);
            return img_files_list;
        }

        private string openDirectory()
        {
            string to_return = "";
            using (var fbd = new System.Windows.Forms.FolderBrowserDialog())
            {
                System.Windows.Forms.DialogResult result = fbd.ShowDialog();
                if (result == System.Windows.Forms.DialogResult.OK)
                {
                    to_return = fbd.SelectedPath;
                }
                else if(!string.IsNullOrWhiteSpace(fbd.SelectedPath))
                {
                    string messageBoxText = "Could not open the directory.";
                    string caption = "Invalid directory";
                    MessageBoxButton button = MessageBoxButton.OK;
                    MessageBoxImage icon = MessageBoxImage.Warning;

                    // Display message box
                    System.Windows.MessageBox.Show(messageBoxText, caption, button, icon);

                }
            }
            return to_return;
        }

        private void imageSequenceFileOpenClick(object sender, RoutedEventArgs e)
        {
            // First clean up existing tracking
            StopTracking();

            string directory = openDirectory();
            if (!string.IsNullOrWhiteSpace(directory))
            {
                SequenceReader reader = new SequenceReader(directory, true, fx, fy, cx, cy);

                processing_thread = new Thread(() => ProcessSequence(reader));
                processing_thread.Name = "Image sequence processing";
                processing_thread.Start();
            }

        }

        private void videoFileOpenClick(object sender, RoutedEventArgs e)
        {
            // First clean up existing tracking
            StopTracking();

            var video_files = openMediaDialog(false);
            processing_thread = new Thread(() => ProcessSequences(video_files));
            processing_thread.Name = "Video processing";
            processing_thread.Start();

        }

        // Selecting one or more images in a directory
        private void individualImageFilesOpenClick(object sender, RoutedEventArgs e)
        {
            // First clean up existing tracking
            StopTracking();

            var image_files = openMediaDialog(true);

            if(image_files.Count > 0)
            { 
                ImageReader reader = new ImageReader(image_files, fx, fy, cx, cy);

                processing_thread = new Thread(() => ProcessIndividualImages(reader));
                processing_thread.Start();
            }
        }

        // Selecting a directory containing images
        private void individualImageDirectoryOpenClick(object sender, RoutedEventArgs e)
        {
            
            // First clean up existing tracking
            StopTracking();

            string directory = openDirectory();
            if(!string.IsNullOrWhiteSpace(directory))
            { 
                ImageReader reader = new ImageReader(directory, fx, fy, cx, cy);

                processing_thread = new Thread(() => ProcessIndividualImages(reader));
                processing_thread.Start();
            }
        }

        private void openWebcamClick(object sender, RoutedEventArgs e)
        {
            StopTracking();

            // If camera selection has already been done, no need to re-populate the list as it is quite slow
            if (cam_sec == null)
            {
                cam_sec = new CameraSelection();
            }
            else
            {
                cam_sec = new CameraSelection(cam_sec.cams);
                cam_sec.Visibility = System.Windows.Visibility.Visible;
            }

            // Set the icon
            Uri iconUri = new Uri("logo1.ico", UriKind.RelativeOrAbsolute);
            cam_sec.Icon = BitmapFrame.Create(iconUri);

            if (!cam_sec.no_cameras_found)
                cam_sec.ShowDialog();

            if (cam_sec.camera_selected)
            {
                int cam_id = cam_sec.selected_camera.Item1;
                int width = cam_sec.selected_camera.Item2;
                int height = cam_sec.selected_camera.Item3;

                SequenceReader reader = new SequenceReader(cam_id, width, height, fx, fy, cx, cy);

                processing_thread = new Thread(() => ProcessSequence(reader));
                processing_thread.Name = "Webcam processing";
                processing_thread.Start();

            }
        }


        // --------------------------------------------------------
        // Button handling
        // --------------------------------------------------------

        // Cleanup stuff when closing the window
        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            if (processing_thread != null)
            {
                // Stop capture and tracking
                thread_running = false;
                processing_thread.Join();
            }
            // Added by Huang
            pubSocket.Close();        
        }

        // Stopping the tracking
        private void StopButton_Click(object sender, RoutedEventArgs e)
        {
            if (processing_thread != null)
            {
                // Stop capture and tracking
                thread_paused = false;
                thread_running = false;
                // Let the processing thread finish
                processing_thread.Join();

                // Clean up the interface
                EndMode();
            }
        }

        private void PauseButton_Click(object sender, RoutedEventArgs e)
        {
            if (processing_thread != null)
            {
                // Stop capture and tracking                
                thread_paused = !thread_paused;

                NextFrameButton.IsEnabled = thread_paused;
                NextFiveFramesButton.IsEnabled = thread_paused;

                if (thread_paused)
                {
                    PauseButton.Content = "Resume";
                }
                else
                {
                    PauseButton.Content = "Pause";
                }
            }
        }

        private void SkipButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender.Equals(NextFrameButton))
            {
                skip_frames += 1;
            }
            else if (sender.Equals(NextFiveFramesButton))
            {
                skip_frames += 5;
            }
        }


        private void VisualisationChange(object sender, RoutedEventArgs e)
        {
            // Collapsing or restoring the windows here
            if (!ShowTrackedVideo)
            {
                VideoBorder.Visibility = System.Windows.Visibility.Collapsed;
                MainGrid.ColumnDefinitions[0].Width = new GridLength(0, GridUnitType.Star);
            }
            else
            {
                VideoBorder.Visibility = System.Windows.Visibility.Visible;
                MainGrid.ColumnDefinitions[0].Width = new GridLength(2.1, GridUnitType.Star);
            }

            if (!ShowAppearance)
            {
                AppearanceBorder.Visibility = System.Windows.Visibility.Collapsed;
                MainGrid.ColumnDefinitions[1].Width = new GridLength(0, GridUnitType.Star);
            }
            else
            {
                AppearanceBorder.Visibility = System.Windows.Visibility.Visible;
                MainGrid.ColumnDefinitions[1].Width = new GridLength(0.8, GridUnitType.Star);
            }

            // Collapsing or restoring the windows here
            if (!ShowGeometry)
            {
                GeometryBorder.Visibility = System.Windows.Visibility.Collapsed;
                MainGrid.ColumnDefinitions[2].Width = new GridLength(0, GridUnitType.Star);
            }
            else
            {
                GeometryBorder.Visibility = System.Windows.Visibility.Visible;
                MainGrid.ColumnDefinitions[2].Width = new GridLength(1.0, GridUnitType.Star);
            }

            // Collapsing or restoring the windows here
            if (!ShowAUs)
            {
                ActionUnitBorder.Visibility = System.Windows.Visibility.Collapsed;
                MainGrid.ColumnDefinitions[3].Width = new GridLength(0, GridUnitType.Star);
            }
            else
            {
                ActionUnitBorder.Visibility = System.Windows.Visibility.Visible;
                MainGrid.ColumnDefinitions[3].Width = new GridLength(1.6, GridUnitType.Star);
            }

        }
       
        private void setOutputImageSize_Click(object sender, RoutedEventArgs e)
        {

            NumberEntryWindow number_entry_window = new NumberEntryWindow(image_output_size);
            number_entry_window.Icon = this.Icon;

            number_entry_window.WindowStartupLocation = WindowStartupLocation.CenterScreen;

            if (number_entry_window.ShowDialog() == true)
            {
                image_output_size = number_entry_window.OutputInt;
            }
        }

        private void ExclusiveMenuItem_Click(object sender, RoutedEventArgs e)
        {
            // Disable all other items but this one
            MenuItem parent = (MenuItem)((MenuItem)sender).Parent;
            foreach (var me in parent.Items)
            {
                ((MenuItem)me).IsChecked = false;
            }
            ((MenuItem)sender).IsChecked = true;

        }

        private void setCameraParameters_Click(object sender, RoutedEventArgs e)
        {
            CameraParametersEntry camera_params_entry_window = new CameraParametersEntry(fx, fy, cx, cy);
            camera_params_entry_window.Icon = this.Icon;

            camera_params_entry_window.WindowStartupLocation = WindowStartupLocation.CenterScreen;

            if (camera_params_entry_window.ShowDialog() == true)
            {
                fx = camera_params_entry_window.Fx;
                fy = camera_params_entry_window.Fy;
                cx = camera_params_entry_window.Cx;
                cy = camera_params_entry_window.Cy;
            }
        }

        // Making sure only one radio button is selected
        private void MenuItemWithRadioButtons_Click(object sender, System.Windows.RoutedEventArgs e)
        {
            MenuItem mi = sender as MenuItem;
            if (mi != null)
            {
                RadioButton rb = mi.Icon as RadioButton;
                if (rb != null)
                {
                    rb.IsChecked = true;
                }
            }
        }

        private void OutputLocationItem_Click(object sender, RoutedEventArgs e)
        {
            var dlg = new CommonOpenFileDialog();
            dlg.Title = "Select output directory";
            dlg.IsFolderPicker = true;
            dlg.AllowNonFileSystemItems = false;
            dlg.EnsureFileExists = true;
            dlg.EnsurePathExists = true;
            dlg.EnsureReadOnly = false;
            dlg.EnsureValidNames = true;
            dlg.Multiselect = false;
            dlg.ShowPlacesList = true;

            if (dlg.ShowDialog() == CommonFileDialogResult.Ok)
            {
                var folder = dlg.FileName;
                record_root = folder;
            }
        }

    }

}
