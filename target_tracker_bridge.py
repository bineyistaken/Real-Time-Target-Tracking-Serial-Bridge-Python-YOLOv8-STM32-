import cv2
import serial
import time

PORT = 'COM3'
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.05)
    print(f"[+] Connected to {PORT} successfully.")
    time.sleep(1)
except Exception as e:
    print(f"[-] Failed to open serial port: {e}")
    exit()

cap = cv2.VideoCapture(0)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

CENTER_X = FRAME_WIDTH // 2
CENTER_Y = FRAME_HEIGHT // 2

target_x, target_y = CENTER_X, CENTER_Y

def mouse_click(event, x, y, flags, param):
    global target_x, target_y
    if event == cv2.EVENT_LBUTTONDOWN:
        target_x, target_y = x, y

cv2.namedWindow("Target Tracking Bridge")
cv2.setMouseCallback("Target Tracking Bridge", mouse_click)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    delta_x = target_x - CENTER_X
    delta_y = target_y - CENTER_Y

    # Frame packet: <X,Y>\n
    packet = f"<{delta_x},{delta_y}>\n"
    ser.write(packet.encode('utf-8'))

    # Read parse verification / telemetry from STM32
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8', errors='ignore').strip()
        if response:
            print(f"STM32 Response: {response}")

    # Visual telemetry overlays
    cv2.drawMarker(frame, (CENTER_X, CENTER_Y), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
    cv2.circle(frame, (target_x, target_y), 8, (0, 0, 255), -1)
    cv2.line(frame, (CENTER_X, CENTER_Y), (target_x, target_y), (255, 255, 0), 1)
    cv2.putText(frame, f"Sent: {packet.strip()}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Target Tracking Bridge", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()