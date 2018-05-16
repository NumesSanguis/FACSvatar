using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class sphereAttach : MonoBehaviour {

    public GameObject parent;
	
	// Update is called once per frame
	void Update () {
        gameObject.transform.SetParent(parent.transform);
	}
}
