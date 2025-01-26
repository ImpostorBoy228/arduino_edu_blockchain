import serial
import requests
import json
from threading import Thread

SERVER_URL = "http://localhost:5000"
ARDUINO_PORT = "COM4"  # Замените на ваш порт

ser = serial.Serial(ARDUINO_PORT, 115200, timeout=1)

def handle_arduino():
    while True:
        if ser.in_waiting:
            line = ser.readline().decode().strip()
            try:
                solution = json.loads(line)
                response = requests.post(f"{SERVER_URL}/submit", json=solution)
                print(f"Submission result: {response.json()}")
            except Exception as e:
                print(f"Error: {str(e)}")

def send_jobs():
    while True:
        try:
            job = requests.get(f"{SERVER_URL}/mine").json()
            ser.write((json.dumps(job) + '\n').encode())
        except Exception as e:
            print(f"Error getting job: {str(e)}")

if __name__ == "__main__":
    Thread(target=handle_arduino).start()
    Thread(target=send_jobs).start()