using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HeadCullingFPS : MonoBehaviour {

    public bool headCam;
    private Camera cameraRef;
    private string arma;
    //private Transform arma;
    //private GameObject arma;

    // Use this for initialization
    void Start () {
        cameraRef = gameObject.GetComponentInChildren<Camera>();
        // get _armature game object of human model
        foreach (Transform child in transform)
        //foreach (GameObject child in transform)
        {
            if (child.name.EndsWith("_armature"))
            {
                arma = child.name;
                break;
            }
        }

        // attach camera to neck for pose rotation data
        cameraRef.transform.SetParent(GameObject.Find(gameObject.name + "/" + arma + "/root/pelvis/spine01/spine02/spine03/neck").transform);  // /head
        // transform.GetChild(1).name
        HeadCull();
	}

    public void HeadCull()
    {

        if (headCam == true)
        {
            cameraRef.enabled = true;
            // scale head to zero to prevent interference with camera view
            //GameObject.Find(arma + "/root/pelvis/spine01/spine02/spine03/neck/head").transform.localScale = Vector3.zero;  // /head
        }
        else
        {
            cameraRef.enabled = false;
            // scale head back to normal size
            //GameObject.Find(arma + "/root/pelvis/spine01/spine02/spine03/neck/head").transform.localScale = Vector3.one;  // /head
        }
    }

}
