import os
os.sys.path
import cv2
import numpy as np
import time
import subprocess
from IPython.display import display, clear_output, FileLink, Image

time_yellow = []
time_orange = []
time_green = []
time_white = []
quad_yellow = []
quad_orange = []
quad_green = []
quad_white = []
record = []

start_time = time.time()

# File to write data
output_text_file = "ball_tracking_data.txt"
f = open(output_text_file, "w")

color = ["yellow", "orange", "green", "white"]

# Function to determine quadrant based on coordinates
def determine_quadrant(x, y):
    if 1260 < x < 1740:
        return 1 if 540 < y < 1000 else 4
    elif 790 < x < 1222:
        return 2 if 540 < y < 1010 else 3
    return None

input_video = '/Users/jesicaanniebijju/Downloads/AI Assignment video.mp4'
cap = cv2.VideoCapture(input_video)

# Video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

output_video = 'labeled_output_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (17, 17), 0)

    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1.4, 90, param1=100,
                               param2=35, minRadius=10, maxRadius=80)

    if circles is not None:
        circles = np.uint16(np.around(circles))

        for (x, y, rad) in circles[0, :]:
            cv2.circle(frame, (x, y), rad, (100, 255, 0), 3)
            b, g, r = frame[y, x]

            # Detection and tracking
            color_detected = None
            if 57 < r < 213 and 52 < g < 189 and 15 < b < 63:
                color_detected = "yellow"
                quad_yellow.append(determine_quadrant(x, y))
                time_yellow.append(int(time.time() - start_time))
            elif 12 < r < 55 and 41 < g < 77 and 34 < b < 69:
                color_detected = "green"
                quad_green.append(determine_quadrant(x, y))
                time_green.append(int(time.time() - start_time))
            elif 176 < r < 255 and 61 < g < 167 and 29 < b < 131:
                color_detected = "orange"
                quad_orange.append(determine_quadrant(x, y))
                time_orange.append(int(time.time() - start_time))
            elif 113 < r < 248 and 111 < g < 246 and 94 < b < 226:
                color_detected = "white"
                quad_white.append(determine_quadrant(x, y))
                time_white.append(int(time.time() - start_time))

            if color_detected:
                current_quad = locals()[f"quad_{color_detected}"][-1]
                current_time = locals()[f"time_{color_detected}"][-1]
                
                # Labelling frame
                cv2.putText(frame, f'Quad: {current_quad}, Color: {color_detected}', (x - 50, y - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                if len(locals()[f"time_{color_detected}"]) > 1:
                    prev_time = locals()[f"time_{color_detected}"][-2]
                    if current_time - prev_time > 1:
                        entry = f"{prev_time}, {current_quad}, {color_detected}, Entry\n"
                        exit = f"{current_time}, {current_quad}, {color_detected}, Exit\n"
                        f.write(entry)
                        f.write(exit)
                        locals()[f"time_{color_detected}"].clear()
                        locals()[f"quad_{color_detected}"].clear()

    out.write(frame)

    cv2.imshow('Squares and Circles', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

f.close()

print(f"Processed video saved as: {output_video}")
print(f"Ball tracking data saved as: {output_text_file}")