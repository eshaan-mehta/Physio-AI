from setup import *

OVERLAY_HEIGHT = 100
FRAME_INTERVAL = 5

MIN_CONFIDENCE = 0.5
ANIM_FRAMES = 12

UP_THRESHOLD = 150
DOWN_THRESHOLD = 110
STRAIGHTNESS_THRESHOLD = 65
FRONT_knee_THRESHOLD = 87


STATUS_LIST = {0:"OFF", 1:"RESET", 2:"ACTIVE", 3:"END"}
STATUS_COLOR = {0:(0,0,0), 1:(0,0,160), 2:(0,190,0), 3:(153,51,102)}
status = 0

PATH = "graphs/depth.png"

front_knee = []
back_knee = []
back_side = []
front_leg = ""

def reset() -> None:
    global front_knee_angle, back_knee_angle, hip_angle
    global back_straightness, knee_to_ankle_x, depth, num_reps, is_up
    global straightness_warnings, knee_warnings, frames, depth_points, rep_points, frame_count
    global anim_count_back, anim_count_knee, is_graph_created

    try:
        remove(PATH)
    except:
        pass

    front_knee_angle = 0
    back_knee_angle = 0
    hip_angle = 0

    back_straightness = 0 #percentage
    
    #points for analytics
    straightness_warnings = 0
    knee_warnings = 0
    frames = []
    depth_points = []
    rep_points = []
    frame_count = 0

    anim_count_back = 0
    anim_count_knee = 0
    is_graph_created = False

    num_reps = 0
    is_up = True


def find_angle(start: list, middle: list, end: list) -> float:
    #calculate angle and convert to degrees
    angle = arctan2(start[1] - middle[1], start[0] - middle[0]) - arctan2(end[1] - middle[1], end[0] - middle[0])
    angle = abs(angle * 180/pi)

    #ensures angle between 0-180 degrees
    return (360 - angle) if angle > 180 else angle

def deviation(target: float, range: float, angle: float) -> float:
    #converts angle to percentage based of deviation from specified target
    # maps angle to [0,1] * 100

    percent = 1 - abs(target - angle)/range

    return 0 if (target - angle > range) else round(percent*100, 2)

def create_graph():
    plt.clf()
    plt.plot(frames, depth_points, color = 'b')

    plt.xticks(rep_points, (f"{i+1}" for i in range(len(rep_points))))
    plt.xlabel("Reps")
    plt.ylabel("Height")
    plt.title("Depth and Rep Analytics")

    for point in rep_points:
        plt.axvline(x=point, color = 'r', label = "axvline - full height")

    plt.savefig(PATH)
    #plt.show()

def graph_overlay(frame: cv.Mat) -> cv.Mat:
    w, h = frame.shape[1]//3*2, frame.shape[0]//3*2
    x_off, y_off = (frame.shape[1] - w)//2, (frame.shape[0] - h)//2 

    try:
        img = cv.imread(PATH)
    except:
        print("graph not found")
        return
        
    img = cv.resize(img, (w, h))

    frame[y_off:y_off+h, x_off:x_off+w] = img

    return frame

def overlay(frame: cv.Mat) -> cv.Mat:
    #frame shape = (height, width, depth)
    #color is in BGR
    
    #status background
    frame = cv.rectangle(img=frame,
                         pt1=(frame.shape[1]//4*3, 0),
                         pt2=(frame.shape[1], frame.shape[0]//10),
                         color=STATUS_COLOR[status],
                         thickness=cv.FILLED
                         )
    #status text
    frame = cv.putText(img=frame,
                       text=STATUS_LIST[status],
                       org=(frame.shape[1]//4*3 + 25, 50),
                       fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                       fontScale=2.5,
                       color=(255,255,255),
                       thickness=2)

#-----------------------------------------------------------------------------
    
    #rep background
    frame = cv.rectangle(img=frame,
                         pt1=(0,0),
                         pt2=(frame.shape[1]//3, frame.shape[0]//10),
                         color=(160,0,0),
                         thickness=cv.FILLED
                         )
    
    #rep counter
    frame = cv.putText(img=frame,
                       text=f"Reps: {num_reps}",
                       org=(25, 50),
                       fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                       fontScale=2.5,
                       color=(255,255,255),
                       thickness=2)
    
    if status != 3:
        #up/down status
        frame = cv.putText(img=frame,
                        text= "up" if is_up else "down",
                        org=(300, 50),
                        fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale= 1.7,
                        color=(255,255,255),
                        thickness=1)

#-----------------------------------------------------------------------------

    #bottom background rectangle
    frame = cv.rectangle(img=frame,
                         pt1=(0, frame.shape[0] - OVERLAY_HEIGHT),
                         pt2=(frame.shape[1], frame.shape[0]),
                         color=(0,0,0),
                         thickness=cv.FILLED
                         )
    if status == 3:
        frame = cv.putText(img=frame,
                        text=f"Total Back Warnings: {straightness_warnings}",
                        org=(25, frame.shape[0] - OVERLAY_HEIGHT + 35),
                        fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale=1.2,
                        color=(255,255,255),
                        thickness=2)
        
        frame = cv.putText(img=frame,
                        text=f"Total Knee Warnings: {knee_warnings}",
                        org=(frame.shape[1]//2 + 25, frame.shape[0] - OVERLAY_HEIGHT + 35),
                        fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale=1.2,
                        color=(255,255,255),
                        thickness=2)  
    else:
        #front knee angle text
        frame = cv.putText(img=frame,
                        text=f"Front Knee Angle: {round(front_knee_angle, 2)}",
                        org=(25, frame.shape[0] - OVERLAY_HEIGHT + 25),
                        fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale=1.2,
                        color=(255,255,255),
                        thickness=2)
        
        #back knee angle text
        frame = cv.putText(img=frame,
                        text=f"Back Knee Angle: {round(back_knee_angle, 2)}",
                        org=(25, frame.shape[0] - OVERLAY_HEIGHT + 65),
                        fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale=1.2,
                        color=(255,255,255),
                        thickness=2)
        
        #back straightness
        frame = cv.putText(img=frame,
                        text=f"Back Straighness: {back_straightness}%",
                        org=(frame.shape[1]//3*2, frame.shape[0] - OVERLAY_HEIGHT + 25),
                        fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale=1.2,
                        color=(255,255,255),
                        thickness=2)
        
        #front leg
        frame = cv.putText(img=frame,
                        text=f"Front leg: {front_leg}",
                        org=(frame.shape[1]//3, frame.shape[0] - OVERLAY_HEIGHT//2),
                        fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale=1.2,
                        color=(255,255,255),
                        thickness=2)

        #balance
        frame = cv.putText(img=frame,
                        text=f"Hip Angle: {round(hip_angle, 2)}",
                        org=(frame.shape[1]//3*2, frame.shape[0] - OVERLAY_HEIGHT + 65),
                        fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale=1.2,
                        color=(255,255,255),
                        thickness=2)
    
    return frame
    
def add_warning(frame: cv.Mat, warning_type: int) -> cv.Mat:
    #straightness warning
    if warning_type == 1:    
        frame = cv.putText(img=frame,
                            text="STRAIGHTEN BACK",
                            org=(int(back_side[0][0]), int(back_side[0][1])),
                            fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                            fontScale=2.8,
                            color=(15,15,255),
                            thickness=3)
    else: #front knee warning
        frame = cv.putText(img=frame,
                            text="MOVE FRONT KNEE BACK",
                            org=(int(front_knee[1][0]), int(front_knee[1][1])),
                            fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,
                            fontScale=2.8,
                            color=(0, 216, 255),
                            thickness=3)
        
    return frame


reset()
while capture.isOpened():
    success, frame = capture.read() #extracts single frame from video, success if receiving video

    if not success:
        print("failed")
        break
    
    results = model(source=frame, verbose=False, conf=MIN_CONFIDENCE)
    
    for person in results:
        #index 0 to go down one dimension within tensor
        #bring keypoints back to cpu and convert to list
        keypoints = person.keypoints.xy[0].cpu().tolist() 

        #use try, except block to prevent crashes if error arises for a frame
        try:  
            #-------- FRONT/BACK KEYPOINT DETECTION ----------------------
            if keypoints[1][0] < keypoints[3][0]: #user facing camera left
                if keypoints[15][0] < keypoints[16][0]: #left leg forward
                    front_knee = [keypoints[11], keypoints[13], keypoints[15]] #left
                    back_knee = [keypoints[12], keypoints[14], keypoints[16]] #right
                    back_side = [keypoints[5], keypoints[11], keypoints[14]] #right
                    front_leg = "Left"

                else: #right leg forward
                    front_knee = [keypoints[12], keypoints[14], keypoints[16]] #right
                    back_knee = [keypoints[11], keypoints[13], keypoints[15]] #left
                    back_side = [keypoints[6], keypoints[12], keypoints[13]] #left
                    front_leg = "Right"
            if keypoints[1][0] >= keypoints[3][0]: #user facing camera right
                if keypoints[15][0] > keypoints[16][0]: #left leg forward
                    front_knee = [keypoints[11], keypoints[13], keypoints[15]] #left
                    back_knee = [keypoints[12], keypoints[14], keypoints[16]] #right
                    back_side = [keypoints[5], keypoints[11], keypoints[14]] #right
                    front_leg = "Left"

                else: #right leg forward
                    front_knee = [keypoints[12], keypoints[14], keypoints[16]] #right
                    back_knee = [keypoints[11], keypoints[13], keypoints[15]] #left
                    back_side = [keypoints[6], keypoints[12], keypoints[13]] #left
                    front_leg = "Right"
            
            
            #----------- ACTIVE MODE -------------------
            if status == 2:
                #----------- STAT CALCULATIONS -----------
                #calculating angles at knees, hip
                front_knee_angle = find_angle(front_knee[0], front_knee[1], front_knee[2])
                back_knee_angle = find_angle(back_knee[0], back_knee[1], back_knee[2])
                hip_angle = find_angle(back_side[0], back_side[1], back_side[2])

                #calculate back straighness using hip angle
                back_straightness = deviation(142 if is_up else 157, 60, hip_angle)

                #----------- REP COUNTING --------------------------
                if front_knee_angle > UP_THRESHOLD and not is_up:
                    num_reps += 1
                    is_up = True

                    rep_points.append(frame_count)
                elif is_up and (front_knee_angle < DOWN_THRESHOLD):
                    is_up = False

                #----------- WARNING DETECTION AND OVERLAY ----------  
                #detect poor back straightness
                if back_straightness < STRAIGHTNESS_THRESHOLD and not is_up and anim_count_back == 0:
                    straightness_warnings += 1
                    anim_count_back = 1

                #detect front knee too far forward
                if front_knee_angle < FRONT_knee_THRESHOLD and not is_up and anim_count_knee == 0:
                    knee_warnings += 1
                    anim_count_knee = 1
                    
            

                # ----------- FRAME COUNTING ---------------------------
                frame_count += 1
                if frame_count % 3 == 0:
                    frames.append(frame_count)
                    depth_points.append(frame.shape[0] - front_knee[0][1])
            
            #----------- END MODE -------------------
            if status == 3:
                if not is_graph_created:
                    create_graph()
                    is_graph_created = True
                
            #-----------  STATUS UPDATE --------------------------------
            #set status to reset if left wrist above shoulder
            #note: y increases as you go down the screen
            if keypoints[9][1] < keypoints[5][1]:
                status = 1
                #reset stats if not already reset
                if front_knee_angle > 0:
                    reset()

            elif keypoints[10][1] < keypoints[6][1]: #set status to quit if right wrist above shoulder
                status = 3
            else: 
                if status == 1: #set to active status after reset
                    status = 2
        except:
            pass
        
        annotated_frame = person.plot() #adding person bounding box to frame 

    #---------- DISPLAY WARNING ------------
    #display back warning
    if anim_count_back > 0  and anim_count_back < ANIM_FRAMES:
        annotated_frame = add_warning(annotated_frame, 1)
        anim_count_back += 1
    elif anim_count_back >= ANIM_FRAMES:
        anim_count_back = 0

    #display knee warning
    if anim_count_knee > 0  and anim_count_knee < ANIM_FRAMES:
        annotated_frame = add_warning(annotated_frame, 2)
        anim_count_knee += 1
    elif anim_count_knee >= ANIM_FRAMES:
        anim_count_knee = 0

    annotated_frame = overlay(annotated_frame) #adding all overlay

    if is_graph_created:
        annotated_frame = graph_overlay(annotated_frame)
        
    cv.imshow(WINDOW_NAME, annotated_frame) #display frame

    #program waits 1ms each between frames checks for keypress of 'q'
    if (cv.waitKey(1) & 0xFF) == ord('q'):
        break
    

capture.release()
cv.destroyAllWindows()
