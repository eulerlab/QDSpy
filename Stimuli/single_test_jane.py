import os
import sys
import QDS
import QDSpy_global as glo

QDS.Initialize("video_nature1", "Jane's matural movies")

# Ensure the path to stimuli is correctly set
glo.QDSpy_pathStim = os.getcwd()  # assumes water.avi is in current directory

FrRefr_Hz = QDS.GetDefaultRefreshRate()
p = {
    "nTrials": 1,
    "vidScale": (1.0, 1.0),
    "vidOrient": 0,
    "vidAlpha": 255,
    "MarkPer_s": 1.0,
    "durFr_s": 1 / FrRefr_Hz,
    "nFrPerMarker": 3,
    #"vidName": "/home/ydeng/Github/QDSpy/Stimuli/test_mix.avi"
    "path": "",
    "ext": ".avi",
    "vidNames": [
        "GUVRatiof1_30Hz_mix_seed0", 
        "GUVRatiof10_30Hz_mix_seed2"   
    ]
}
QDS.LogUserParameters(p)

# Generate a video (clip) list and define video objects
vidList = []
for iVid, vidName in enumerate(p["vidNames"]):
    vid = os.path.join(p["path"], vidName + p["ext"])
    QDS.DefObj_Video(iVid, vid)
    vidParams = QDS.GetVideoParameters(iVid)
    if vidParams: 
        tmp = [iVid, vid, vidParams["nFr"]]
        vidList.append(tmp)
    else:
        print(f"Video `{vid}` was not found - abort.")    
        sys.exit()

QDS.DefObj_Box(100, 600, 600, 0)        
QDS.SetObjColor(1, [100], [(0,128,128)])

# Calculate frame duration, marker duration and interval between markers
dFr = 1 / FrRefr_Hz
dMark_s = p["nFrPerMarker"] * dFr
dInterval_s = 1.0 / p["MarkPer_s"]

# Define clip sequence
clipSeq = [0,1,0,1,1,1,0,0,0]
QDS.LogUserParameters({"Clip sequence": clipSeq})

# Start script and clear the scene
QDS.StartScript()
QDS.Scene_Clear(1.00, 0)

# Iterate over clip list
for iVid in clipSeq:
    # Calculate the number of markers depending on the video clip
    # length (allows for video clips to be of variable length)
    vidID = vidList[iVid][0]
    nFr = vidList[iVid][2]
    nMark = int(nFr / FrRefr_Hz / p["MarkPer_s"])

    QDS.Start_Video(vidID, (0, 0), p["vidScale"], p["vidAlpha"], p["vidOrient"])
    for _ in range(nMark):
        QDS.Scene_Clear(dMark_s, 1)
        QDS.Scene_Clear(dInterval_s - dMark_s, 0)

    # Introduce a break to make sure that the video as finished and it 
    # does not mix with the following video
    if glo.QDSpy_vid_useIter:
        QDS.Scene_Clear(0.05, 0)
        QDS.Scene_Render(0.55, 1, [100], [(0,0)], 0)
    else:    
        QDS.Scene_Render(0.10, 1, [100], [(0,0)], 0)

QDS.Scene_Clear(1.00, 0)
QDS.EndScript()

