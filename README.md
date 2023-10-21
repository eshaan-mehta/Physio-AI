# PhysioAI
# created by: Eshaan Mehta, Darius Rudaitis

This project utilizes YoloV8 Pose, OpenCV, PyTorch, Matplotlib to deliver a cohesive AI powered lunge analyst.

-- File Structure --
* requirements.txt: list of all dependencies needed to run project
* setup.py: install dependencies, move model to appropriate device, create model and video object
* main.py: all code, logic related to project
* yolov8s-pose.pt: model used in project
* graphs: graph pictures are saved here once generated.
    * template.png: template for blank graph


-- Operational instructions -- 
1. Run: pip install -r requirements.txt
2. Run main.py to begin
3. Ensure entire body is in frame, and stand sideways
4. Raise left hand to reset and activate program
5. Perform exercise, watch for warning messages
6. When finished, raise right hand to see graph
7. Raise left hand again to reset and use again
8. Press 'q' on keyboard to close project window

