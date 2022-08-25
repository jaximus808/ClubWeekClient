import UnityCommunicator as U;
import HandController 
import time;
import cv2;
import mediapipe as mp;

dataReader = HandController.Hands();
sock = U.UnityCommunicator("", 8000, 8001,dataReader, "127.0.0.1",8000,True, True,)


t = time.time()
timer = 0
deltaTime = t;
cap = cv2.VideoCapture(0)
while True:
    
    success, img = cap.read()
    img,results = dataReader.handData(img)

    if dataReader.connected:
        data = dataReader.CreateData(results);
        
        sock.SendData(data);
    else:
        t = time.time()
        # print(t)
        # print(deltaTime)
        timer += t - deltaTime; 
        deltaTime = t; 
        if timer > 5:
            timer = 0; 
            data = dataReader.CreateJoinDataDemo();
            sock.SendData(data); 
    if dataReader.connected:
        cv2.putText(img, "connected", (10,70), cv2.FONT_HERSHEY_PLAIN, 3,(255,0,255), 3);
    elif sock.disconnected:
        cv2.putText(img, "Fleet Server Closed", (10,70), cv2.FONT_HERSHEY_PLAIN, 3,(255,0,255), 3);
    else:
        cv2.putText(img, "connecting", (10,70), cv2.FONT_HERSHEY_PLAIN, 3,(255,0,255), 3);
    cv2.imshow("Image",img);
    cv2.waitKey(1);
    # if cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) <1:
    #     print("MEOW")
    #     break  