"""
Main file for the Japan Politics RAG virtual human.

This script starts the Unity connection and runs the main dialogue with the virtual human used for the thesis. 
It connects the use case, experiment settings, speech pipeline, and Unity virtual human interface.

It is not fully runnable from the public repository because several
supervisor-provided files and private configuration files are intentionally excluded.
"""

# create  evironment variables
from dotenv import load_dotenv
load_dotenv()
    
import time
import azure.cognitiveservices.speech as speech
from mistralai.client import Mistral
import speechToUnity
import uc026_questionnaire_japan_politics as usecase
import experiment_settings

if __name__ == "__main__":
    print("Start...")
    # initialize experiment settings
    language = experiment_settings.experiment_language()
    gender = experiment_settings.experiment_gender()

    # start Unity server and wait until Unity is connected
    print("Starting server...")
    speechToUnity.start_unity_server()
    while speechToUnity.client is None:
        time.sleep(1)

    print("Starting dialogue...")
    logs = usecase.dialogue_japan_politics()