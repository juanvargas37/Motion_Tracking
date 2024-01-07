![ezgif com-video-to-gif-converter(1)](https://github.com/juanvargas37/Motion_Tracking/assets/68957192/e9ac4b98-8df7-4319-a394-45b494f312db)

Functionality
    
    The script captures video and processes frames for motion detection.
    Upon detecting motion, it records the video for a specified duration or until motion stops.
    When the recording stops, it compiles the video and sends an email with the video file attached.
    The script adds informative text overlays on the video for real-time monitoring.
   

This part of the code needs to be filled for the code to work:

    #Email setup
    email_sender = "your_email@gmail.com"
    email_password = 'your_password'
    email_receiver = 'receiver_email@gmail.com'

PRESS Q TO EXIT

Run the script in a Python environment:
python motion_detection.py
The script will start capturing video from the default camera. When motion is detected, it will record the video and, upon completion, send an email with the video attached.
