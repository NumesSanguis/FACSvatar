using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraManager : MonoBehaviour {

    public HeadCullingFPS[] models;
    public Camera overviewCam;
	
	// Update is called once per frame
	void Update () {
        if (Input.GetKeyUp(KeyCode.Alpha1))
        {
            ClearCulls();
            models[0].headCam = true;
            models[0].HeadCull();
        }
		if (Input.GetKeyUp(KeyCode.Alpha2))
        {
            ClearCulls();
            models[1].headCam = true;
            models[1].HeadCull();
        }
        //
        if (Input.GetKeyUp(KeyCode.Alpha0))
        {
            ClearCulls();
            Camera.SetupCurrent(overviewCam);
        }
	}

    void ClearCulls()
    {
        foreach(HeadCullingFPS aModel in models)
        {
            aModel.headCam = false;
            aModel.HeadCull();
        }
    }
}
