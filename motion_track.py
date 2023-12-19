import cv2
import imutils
import numpy as np
from datetime import datetime
from collections import deque
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
import re
import os
def main():
    #selects the camera, default to 0 which should be the default camera for system
    cap = cv2.VideoCapture(0)
    #sometimes these are not set so they need to be defaulted to something. 
    video_file_paths = []

    prev_frame = None
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    video_file_path = ''
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None
    email_sender = "breakingandentering3@gmail.com"
    # USE THE DEVICE PASSWORD HERE(is there a way to encrypt this)
    email_password = 'vqdgnnyrxgifpmtz'
    email_receiver = 'breakingandentering3@gmail.com' 
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_receiver):
        print('Invalid email address!')
        
      
    continuous_motion = 0
    motion_grace_period = 0
    recording_saved_text_end_time = None
    recording_saved = None
    #we are recording at 20 frames so this saves 10 seconds at 20 frames
    buffer = deque(maxlen=20*10)
    #while the camera can be opened
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        #adds a frame to buffer in case we need it
        buffer.append(frame)
        
        #turn the incoming into greyscale for easier processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if prev_frame is None:
            prev_frame = gray
            continue
        
        #tracking motion using cv2 contours    
        frame_delta = cv2.absdiff(prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        motion_detected = False
        
        for contour in cnts:
        #we only want to detect motion bigger than a certain size, for now its set to 500
            if cv2.contourArea(contour) < 500:
                continue
            #draw the rectangle around the motion detected.
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            motion_detected = True
            
        #we have to have both these updated. contionous motion keeps track how long motion is being detected for
        #motion_grace is needed because the default is to check frame by frame but there is never 10 seconds
        #of motion for each frame, the buffer allows for the motion to be recorded.
        if motion_detected:
            continuous_motion += 1
            motion_grace_period = 0
        else:
            motion_grace_period += 1
            if motion_grace_period <= 2 * 20:
                continuous_motion += 1
            else:
                continuous_motion = 0
                
        #if we get continous motion for at least 10 seconds at 20 frames, we save the file path for the email later
        #and we write the frames out using cv2.video writer
        if continuous_motion >= 10 * 20:
            if out is None:
                timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
                video_file_path = f'{timestamp}_output.avi'
                video_file_paths.append(video_file_path)
                out = cv2.VideoWriter(f'{timestamp}_output.avi', fourcc, 20.0, (frame_width, frame_height))
                
                
                for buffered_frame in buffer:
                    out.write(buffered_frame)

                recording_saved_text_end_time = time.time() + 3
            out.write(frame)

        
        if out is not None and (continuous_motion >= 30 * 20 or continuous_motion == 0):
            out.release()
            out = None

        if recording_saved and time.time() - recording_saved_start <= 3:
            cv2.putText(frame, "Recording Saved", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        motion_duration = f"Motion Duration: {continuous_motion / 20:.2f} sec"
        cv2.putText(frame, motion_duration, (frame_width - 200, frame_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        cv2.imshow('Motion Tracking', frame)
        prev_frame = gray
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    for video_file_path in video_file_paths:
        if os.path.exists(video_file_path):
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')

            subject = "Motion detected on your camera"
            # gather data about the time that motion was detected and include a link to the video record
            body = f'Motion detected at: {current_time}. \n'
            em = MIMEMultipart()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.attach(MIMEText(body, 'plain'))

            # Add the video file as an attachment
            with open(video_file_path, 'rb') as file:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(file.read())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', f'attachment; filename={video_file_path}')
                em.attach(attachment)

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(email_sender, email_password)
                    server.sendmail(email_sender, email_receiver, em.as_string())
                    print("Email sent successfully")
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

        # Delete the video file
        os.remove(video_file_path)

if __name__ == "__main__":
    prev_frame = None
    main()
    