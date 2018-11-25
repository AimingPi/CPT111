#!/usr/bin/env python3
'''

...

'''
from flask import Flask, render_template, Response, request
import cv2
import pyaudio
import threading
import subprocess
import time
import wave
import pigpio

app = Flask(__name__)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
killHouseAudio = 0
pauseHouseStream = 1
killGateAudio = 0
pauseGateStream = 1
startVideoFeed = 0
answeredCall = 0
updateTime = 0
GATE_SIDE_BUTTON_GPIO = 4
HOUSE_INPUT_AUDIO_DEVICE_INDEX = 3
HOUSE_OUTPUT_AUDIO_DEVICE_INDEX = 1
GATE_INPUT_AUDIO_DEVICE_INDEX = 2
GATE_OUTPUT_AUDIO_DEVICE_INDEX = 0
sometest = 0
timeElapsed = 0

class PlayDoorBell(threading.Thread):

    def run(self):
        wav = wave.open('doorbell.wav', 'rb')
        pyAudio = pyaudio.PyAudio()
        stream = pyAudio.open(start=False,
                                        format=pyAudio.get_format_from_width(wav.getsampwidth()),
                                        output_device_index=HOUSE_OUTPUT_AUDIO_DEVICE_INDEX,
                                        channels=wav.getnchannels(),
                                        rate=wav.getframerate(),
                                        input=False,
                                        output=True,
                                        frames_per_buffer=CHUNK)
        data = wav.readframes(1024)
        stream.start_stream()
        while len(data) > 0:
            try:

                stream.write(data)
                data = wav.readframes(1024)
            except Exception as e:
                print(e)
                break

        stream.close()
        pyAudio.terminate()

class PlayAwaySound(threading.Thread):

    def run(self):
        wav = wave.open('awaysound.wav', 'rb')
        pyAudio = pyaudio.PyAudio()
        stream = pyAudio.open(start=False,
                                        format=pyAudio.get_format_from_width(wav.getsampwidth()),
                                        output_device_index=GATE_OUTPUT_AUDIO_DEVICE_INDEX,
                                        channels=wav.getnchannels(),
                                        rate=wav.getframerate(),
                                        input=False,
                                        output=True,
                                        frames_per_buffer=CHUNK)
        data = wav.readframes(1024)
        stream.start_stream()
        while len(data) > 0:
            try:

                stream.write(data)
                data = wav.readframes(1024)
            except Exception as e:
                print(e)
                break

        stream.close()
        pyAudio.terminate()

class HandleGateButtonPress(threading.Thread):
    # pi = pigpio.pi()
    # pi.set_mode(GATE_SIDE_BUTTON_GPIO, pigpio.INPUT)
    global timeElapsed

    timeElapsed = 0

    def run(self):
        global answeredCall
        global pauseGateStream
        while True:
            global timeElapsed
            global sometest
            try:
                # if self.pi.read(GATE_SIDE_BUTTON_GPIO):
                if sometest:
                    timeElapsed = 0
                    playDoorBell = PlayDoorBell()
                    playDoorBell.start()
                    while timeElapsed < 30:
                        if answeredCall:
                            pauseGateStream = 0
                            timeElapsed = 0
                            break
                        time.sleep(1)
                        timeElapsed += 1
                    timeElapsed = 0
                    if pauseGateStream:
                        playAwaySound = PlayAwaySound()
                        playAwaySound.start()
                if answeredCall:
                    break
                time.sleep(0.1)
            except Exception as e:
                print(e)
                break
            # self.pi.stop()

    def shutdown(self):
        global answeredCall
        answeredCall = 1


# HOUSE AUDIO INPUT -> GATE AUDIO OUTPUT


class HouseStream(threading.Thread):
    pyAudio = pyaudio.PyAudio()

    def run(self):
        self.stream = self.pyAudio.open(start=False,
                                        format=FORMAT,
                                        input_device_index=HOUSE_INPUT_AUDIO_DEVICE_INDEX,
                                        output_device_index=HOUSE_OUTPUT_AUDIO_DEVICE_INDEX,
                                        channels=CHANNELS,
                                        rate=RATE,
                                        input=True,
                                        output=True,
                                        frames_per_buffer=CHUNK)
        while True:
            global killHouseAudio
            global pauseHouseStream
            try:
                if killHouseAudio == 1:
                    self.stream.stop_stream()
                    break
                if pauseHouseStream == 1:
                    self.stream.stop_stream()
                elif not self.stream.is_active():
                    pauseHouseStream = 0
                    self.stream.start_stream()

                try:
                    while self.stream.is_active():
                        audiodata = self.stream.read(CHUNK)
                        self.stream.write(audiodata, CHUNK)
                        if pauseHouseStream == 1:
                            self.stream.stop_stream()
                except Exception as e:
                    print(e)
                    break
                time.sleep(0.1)
            except Exception as e:
                print(e)
                break
        self.stream.stop_stream()
        self.shutdown()

    def shutdown(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyAudio.terminate()


# GATE AUDIO INPUT -> HOUSE AUDIO OUTPUT


class GateStream(threading.Thread):
    pyAudio = pyaudio.PyAudio()

    def run(self):
        self.stream = self.pyAudio.open(start=False,
                                        format=FORMAT,
                                        input_device_index=GATE_INPUT_AUDIO_DEVICE_INDEX,
                                        output_device_index=GATE_OUTPUT_AUDIO_DEVICE_INDEX,
                                        channels=CHANNELS,
                                        rate=RATE,
                                        input=True,
                                        output=True,
                                        frames_per_buffer=CHUNK)
        while True:
            global killGateAudio
            global pauseGateStream
            try:
                if killGateAudio == 1:
                    self.stream.stop_stream()
                    break
                if pauseGateStream == 1:
                    self.stream.stop_stream()
                elif not self.stream.is_active():
                    pauseGateStream = 0
                    self.stream.start_stream()

                try:
                    while self.stream.is_active():
                        audiodata = self.stream.read(CHUNK)
                        self.stream.write(audiodata, CHUNK)
                        if pauseGateStream == 1:
                            self.stream.stop_stream()
                except Exception as e:
                    print(e)
                    break
                time.sleep(0.1)
            except Exception as e:
                print(e)
                break
        self.stream.stop_stream()
        self.shutdown()

    def shutdown(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyAudio.terminate()


houseStream = HouseStream()
gateStream = GateStream()
handleGateButtonPress = HandleGateButtonPress()

handleGateButtonPress.start()
houseStream.start()
gateStream.start()


@app.route('/')
def index():
    global updateTime
    return render_template('index.html', updateTime=updateTime)


def video():
    global startVideoFeed
    if startVideoFeed:
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)
    while startVideoFeed:
        try:
            _, frame = cap.read()
            cv2.imwrite('GateStream.jpg', frame)
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + open('GateStream.jpg', 'rb').read() + b'\r\n')
        except Exception as e:
            print(e)
            break


@app.route('/update_answer_btn')
def update_answer_btn():
    if answeredCall == 1:
        return "Hang up"
    if answeredCall == 0 and timeElapsed == 0:
        return "No calls"
    return str(timeElapsed)


@app.route('/start_feed')
def start_feed():
    global startVideoFeed
    startVideoFeed = 1
    return render_template('index.html')


@app.route('/stop_feed')
def stop_feed():
    global startVideoFeed
    startVideoFeed = 0
    return render_template('index.html')


@app.route('/start_audio')
def start_audio():
    global pauseHouseStream
    pauseHouseStream = 0
    return ""


@app.route('/stop_audio')
def stop_audio():
    global pauseHouseStream
    pauseHouseStream = 1
    return ""


@app.route('/shut_down')
def shut_down():
    houseStream.shutdown()
    gateStream.shutdown()
    handleGateButtonPress.shutdown()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return ""


@app.route('/toggle_gate')
def toggle_gate():
    subprocess.call(["python", "GateToggle.py"], shell=True)
    return ""


@app.route('/answer_call')
def answer_call():
    global answeredCall
    global pauseGateStream
    if answeredCall:
        answeredCall = 0
        pauseGateStream = 1
        handleGateButtonPress = HandleGateButtonPress()
        handleGateButtonPress.start()
    else:
        answeredCall = 1
    return ""


@app.route('/video_feed')
def video_feed():
    return Response(video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/test')
def test():
    global sometest
    if sometest:
        sometest = 0
    else:
        sometest = 1
    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True)
