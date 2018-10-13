using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json.Linq;  // JSON reader; https://assetstore.unity.com/packages/tools/input-management/json-net-for-unity-11347

public class HeadRotator : MonoBehaviour {

	//Quaternion rotation = Quaternion.identity;

	//   Human muscle stuff
	HumanPoseHandler humanPoseHandler;
	HumanPose humanPose;
	Animator anim;

	//   Bone stuff
	//Transform head;

	// Muscle name and index lookup (See in Debug Log)
	void LookUpMuscleIndex() {
		string[] muscleName = HumanTrait.MuscleName;
		int i = 0;
		while (i < HumanTrait.MuscleCount)
		{
			Debug.Log(i + ": " + muscleName[i] +
				" min: " + HumanTrait.GetMuscleDefaultMin(i) + " max: " + HumanTrait.GetMuscleDefaultMax(i));
			i++;
		}
	}

	// Set character in fetus position
	void ResetMuscles() {
		// reset all muscles to 0
		for (int i = 0; i < humanPose.muscles.Length; i++)
		{
			//Debug.Log (humanPose.muscles [i]);
			humanPose.muscles[i] = 0;
		}
	}

	// Use this for initialization
	void Start () {
		// https://forum.unity.com/threads/humanposehandler.430354/

		// get attached Animator controller
		anim = GetComponent<Animator>();

		// run this if you want the indexes to muscles on your character
		LookUpMuscleIndex();

		// TODO keeping body above plane
		//Vector3 current_position = transform.position;
		//Vector3 pelvis_position = gameObject.transform.GetChild(4).transform.GetChild(0).transform.GetChild(0);

		// get human pose handler
		humanPoseHandler = new HumanPoseHandler(anim.avatar, transform);
		//humanPoseHandler = GetComponent<HumanPoseHandler>();
		//humanPoseHandler = new HumanPoseHandler(GetComponent<HumanPoseHandler>());
		// get human pose
		//humanPose = new HumanPose();
		//humanPose = humanPoseHandler.GetHumanPose();
		//humanPose = GetComponent<HumanPose>();


		// TODO keeping body above plane
		//humanPose.bodyPosition = current_position;
		//Vector3 new_position = humanPose.bodyPosition;

		//Debug.Log(current_position + " - " + new_position);

		// reference pose to pose handler
		humanPoseHandler.GetHumanPose(ref humanPose);

		// set a specific musle; 9: Neck Nod Down-Up
		//humanPose.muscles[9] = -20f; 
		//Debug.Log(humanPose.muscles[9]);

		// use pose information to actually set the pose;
		humanPoseHandler.SetHumanPose(ref humanPose);
		//Rigidbody.MovePosition ();
	}

	//void OnAnimatorIK() {
	//	anim.SetIKPosition(AvatarIKGoal.);
	//}

	void ChangeMuscleValue(int muscleIdx, float radian) {
		humanPose.muscles[muscleIdx] = radian;
	}
	
	// Update is called once per frame
	//void Update () {
	//	//humanPoseHandler.SetHumanPose(ref humanPose);
	//}

	// Use JSON message to set head rotation and facial expressions;
	// IEnumerator to run in main thread (probably needed for animation)
	public IEnumerator RequestHeadRotation(JObject head_pose)
	{
		// rotate head of character with received x, y, z rotations in radian
		//List<float> head_rotation = new List<float> ();
		//foreach (KeyValuePair<string, JToken> pair in head_pose) {
            //Debug.Log(pair);
            // store head rotation in radian (not degree)
            //head_rotation.Add(float.Parse(pair.Value.ToString()));  // *Rad2Degree
            //head_pose[pair.Key] = float.Parse(pair.Value.ToString());
		//}

		// Rotation OpenFace: https://github.com/TadasBaltrusaitis/OpenFace/wiki/Output-Format
		// pitch (Rx), yaw (Ry), and roll (Rz)

		// Indexes to muscles
		// 9: Neck Nod Down-Up min: -40 max: 40
		// 10: Neck Tilt Left-Right min: -40 max: 40
		// 11: Neck Turn Left-Right min: -40 max: 40
		// 12: Head Nod Down-Up min: -40 max: 40
		// 13: Head Tilt Left-Right min: -40 max: 40
		// 14: Head Turn Left-Right min: -40 max: 40

		//   25% neck rotation, 75% head rotation
		//Debug.Log("Head rotation: " + head_rotation[0] + ", " + head_rotation[1] + ", " + head_rotation[2]);
		// pitch (head up/down); OpenFace returns opposite values, hence *-1
        ChangeMuscleValue(9, head_pose["pose_Rx"].ToObject<float>() * -.5f);
        ChangeMuscleValue(12, head_pose["pose_Rx"].ToObject<float>() * -1);  //  * .75f

		// yaw (turn head left/right)
        ChangeMuscleValue(11, head_pose["pose_Ry"].ToObject<float>() * .5f);
        ChangeMuscleValue(14, head_pose["pose_Ry"].ToObject<float>());  //  * .75f

		// roll
        ChangeMuscleValue(10, head_pose["pose_Rz"].ToObject<float>() * -.5f);
        ChangeMuscleValue(13, head_pose["pose_Rz"].ToObject<float>() * -1);  //  * .75f

		// do the animation
		humanPoseHandler.SetHumanPose(ref humanPose);



		// Bone rotation attempt
		//Debug.Log ("" + head_rotation[0] + ", " + head_rotation[1] + ", " + head_rotation[2]);
		//Quaternion rotation = Quaternion.Euler(new Vector3(head_rotation[0], head_rotation[1], head_rotation[2]));
		//Debug.Log ("" + rotation[0] + ", " + rotation[1] + ", " + rotation[2] + ", " + rotation[3]);
		// head.Rotate (rotation);

		// https://docs.unity3d.com/ScriptReference/Quaternion-eulerAngles.html
		//rotation.eulerAngles = new Vector3 (head_rotation[0], head_rotation[1], head_rotation[2]);

		// Animator.GetBoneTransform()
		//anim.SetBoneLocalRotation(HumanBodyBones.Head, rotation);

		yield return null;
	}
}
