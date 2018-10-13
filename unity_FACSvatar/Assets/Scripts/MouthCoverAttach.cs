using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MouthCoverAttach : MonoBehaviour {

    public GameObject parent;
    public Vector3 specificCoord;
	
	// Update is called once per frame
	void Start () {
        gameObject.transform.SetParent(parent.transform, true);
        transform.position = specificCoord;
	}
}
