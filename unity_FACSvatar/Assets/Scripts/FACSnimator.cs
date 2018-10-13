using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json.Linq;  // JSON reader; https://assetstore.unity.com/packages/tools/input-management/json-net-for-unity-11347

public class FACSnimator : MonoBehaviour {

	// Manuel Bastioni / MakeHuman model
	SkinnedMeshRenderer skinnedMeshRenderer;
	Mesh skinnedMesh;
	int blendShapeCount;
	Dictionary<string, int> blendDict = new Dictionary<string, int>();

	void Awake()
	{
		// get MB / MH model
		skinnedMeshRenderer = GetComponent<SkinnedMeshRenderer>();
		skinnedMesh = GetComponent<SkinnedMeshRenderer>().sharedMesh;
	}

	// Use this for initialization
	void Start () {
		// create dict of all blendshapes this skinnedMesh has
		blendShapeCount = skinnedMesh.blendShapeCount;
		for (int i = 0; i < blendShapeCount; i++) {
			string expression = skinnedMesh.GetBlendShapeName (i);
			//Debug.Log(expression);
			blendDict.Add (expression, i);
		}
	}
	
	// Update is called once per frame
	//void Update () {
	//	
	//}

	// Use JSON message to set head rotation and facial expressions;
	// IEnumerator to run in main thread (needed for SetBlendShapeWeight)
	public IEnumerator RequestBlendshapes(JObject blendJson)
	{
		//   animate character with received Blend Shape values
		// per Blend Shape, pass on new value to character
		foreach (KeyValuePair<string, JToken> pair in blendJson) {
			//Debug.Log(pair);  // Debug.Log verrrryy slow, don't use in production (>100x slower)
			float blend_val = float.Parse(pair.Value.ToString());
			//float blend_val_float = blend_val<float>();
			skinnedMeshRenderer.SetBlendShapeWeight(blendDict[pair.Key], blend_val*100);
		}

		yield return null;
	}
}
