"""
    Robot: F1
    Framework: keras
    Number of networks: 1
    Network type: LSTM
    Predicionts:
        linear speed(v)
        angular speed(w)

    This brain uses LSTM networks based on Keras framework to predict the linear and angular velocity
    of the F1 car. For that task it uses two different LSTM convolutional neural networks, one for v
    and another one for w
"""

import tensorflow as tf
import numpy as np
import cv2
import time
import os

from utils.constants import PRETRAINED_MODELS_DIR, ROOT_PATH
from os import path

PRETRAINED_MODELS = ROOT_PATH + '/' + PRETRAINED_MODELS_DIR + 'dir1/'

# MODEL_LSTM = 'model_lstm_tinypilotnet_cropped_25.h5' # CHANGE TO YOUR NET
# MODEL_LSTM = 'model_lstm_tinypilotnet_cropped_50.h5'
MODEL_LSTM = 'model_lstm_tinypilotnet_cropped_150.h5'
#MODEL_LSTM = 'model_lstm_cropped_1_test.h5'


class Brain:
    """Specific brain for the f1 robot. See header."""

    def __init__(self, sensors, actuators, handler=None):
        """Constructor of the class.

        Arguments:
            sensors {robot.sensors.Sensors} -- Sensors instance of the robot
            actuators {robot.actuators.Actuators} -- Actuators instance of the robot

        Keyword Arguments:
            handler {brains.brain_handler.Brains} -- Handler of the current brain. Communication with the controller
            (default: {None})
        """
        self.motors = actuators.get_motor('motors_0')
        self.camera = sensors.get_camera('camera_0')
        self.handler = handler
        self.cont = 0
        self.inference_times = []
        #os.environ['CUDA_VISIBLE_DEVICES'] = ''
        self.gpu_inferencing = True if tf.test.gpu_device_name() else False
        
        if not path.exists(PRETRAINED_MODELS + MODEL_LSTM):
            print("File " + MODEL_LSTM + " cannot be found in " + PRETRAINED_MODELS)
            
        self.net = tf.keras.models.load_model(PRETRAINED_MODELS + MODEL_LSTM)

    def update_frame(self, frame_id, data):
        """Update the information to be shown in one of the GUI's frames.

        Arguments:
            frame_id {str} -- Id of the frame that will represent the data
            data {*} -- Data to be shown in the frame. Depending on the type of frame (rgbimage, laser, pose3d, etc)
        """
        self.handler.update_frame(frame_id, data)

    def execute(self):
        """Main loop of the brain. This will be called iteratively each TIME_CYCLE (see pilot.py)"""
        self.cont += 1
        
        image = self.camera.getImage().data
        # Normal image size -> (160, 120)
        # Cropped image size -> (60, 160)
        
        # NORMAL IMAGE
        #print((int(image.shape[1] / 4), int(image.shape[0] / 4)))
        #img = cv2.resize(image, (int(image.shape[1] / 4), int(image.shape[0] / 4)))
        
        # CROPPED IMAGE
        try:
            image = image[240:480, 0:640]
            img = cv2.resize(image, (int(image.shape[1] / 4), int(image.shape[0] / 4)))
            img = np.expand_dims(img, axis=0)
            
            start_time = time.time()
            prediction = self.net.predict(img)
            #print(time.time() - start_time)
            self.inference_times.append(time.time() - start_time)
            prediction_v = prediction[0][0] * 0.5
            #prediction_v = prediction[0][0]
            prediction_w = prediction[0][1]

            if prediction_w != '' and prediction_w != '':
                self.motors.sendV(prediction_v)
                self.motors.sendW(prediction_w)
        except:
            pass

        self.update_frame('frame_0', image)
