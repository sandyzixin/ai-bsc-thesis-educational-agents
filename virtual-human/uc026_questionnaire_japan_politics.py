"""
Use case for the Japan Politics RAG questionnaire.

This script implementes the main dialogue with the virtual human used for the thesis.
It connects the RAG backend, Mistral LLM, speech pipeline, and Unity virtual human interface.

It is not fully runnable from the public repository because several
supervisor-provided files and private configuration files are intentionally excluded.
"""
import time
import csv
import re
import os
import random
import datetime
from mistralai.client import Mistral
import numpy as np
import experiment_settings
import speechToUnity
import utils
import config_mistral
import statements
from RAG.rag import RAG
from mistral_prompt import ask_mistral

# Logging
log_data = []
eval_data = []
def log_string(speaker: str, spoken_text: str):
    """Adds a timestap and dialogue to the dialogue log."""
    current_time = datetime.datetime.now().isoformat(timespec="seconds")
    log_data.append((current_time, speaker, spoken_text))

def log_eval(metrics: dict, query: str, answer: str):
    """Adds evaluation metrics for a generated answer to the evaluation log."""
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    eval_data.append((
        timestamp,
        query,
        answer,
        metrics["answer_query_similarity"],
        metrics["answer_context_similarity"],
        metrics["overlap_count"],
        metrics["overlap_pct"]
    ))

def save_log_to_csv():
    """Saves the dialogue log and RAG evaluation log as CSV files with timestamp."""
    os.makedirs("logs", exist_ok=True)
    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Dialogue log
    dialogue_file = f"logs/VH_dialogue_{session_id}.csv"
    with open(dialogue_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["timestamp", "speaker", "text"])
        writer.writerows(log_data)

    # Eval log
    eval_file = f"logs/VH_eval_{session_id}.csv"
    with open(eval_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["timestamp", "query", "answer", "query_similarity", "context_similarity", "overlap_count", "overlap_pct"])
        writer.writerows(eval_data)

    print(f"Logs saved: {dialogue_file} | {eval_file}")

# Main dialogue function with Mistral
def dialogue_japan_politics():
    """Run the virtual human dialogue flow for the Japan politics RAG use case."""
    language_code = experiment_settings.experiment_language_code()
    language = experiment_settings.experiment_language()
    
    # Initialize strings and questions
    if language == "nl":
        text_strings = statements.nl_text_strings
        display_strings = statements.nl_display_text_strings
        follow_up_questions = statements.nl_follow_up_questions
    elif language == "en":
        text_strings = statements.en_text_strings
        display_strings = statements.en_display_text_strings
        follow_up_questions = statements.en_follow_up_questions
        
    # Initiate Microsoft Azure STT:
    print("Initializing Azure STT with language: " + language_code)
    speech_recognizer = utils.init_ms_azure_stt(language_code)
    print("Azure STT initialized.")

    # Initiate Mistral client
    print("Getting Mistral credentials...")
    my_api_key = config_mistral.get_mistral_key()
    client = Mistral(api_key=my_api_key)
    print("Mistral client initialized.")
    language_google = experiment_settings.experiment_language()
    gender_google = experiment_settings.experiment_gender()
    print("Language: " + language_google + " | Gender: " + gender_google)

    # Dialogue partner names
    avatar_name = display_strings['Avatar']
    user_name = display_strings['You']
    
    # RAG preprocessing
    print("Start the pre-process chunking")
    print("Setting configuration data")
    document_path = "japan_politics.txt"
    embed_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    top_k = 3   # how many chunks to retrieve
    rag_model = RAG(document_path, embed_model)
    rag_model.preprocess()
    
    # Avatar saying welcome
    welcome_statement = text_strings['greeting']
    print(f"{avatar_name}:> {welcome_statement}")
    log_string(avatar_name, welcome_statement)
    speechToUnity.say_something(welcome_statement, language_google, gender_google)
    while speechToUnity.is_speaking:
        time.sleep(0.1)
    
    
    # Avatar saying introduction  
    introduction_statement = text_strings['introduction']
    print(f"{avatar_name}:> {introduction_statement}")
    log_string(avatar_name, introduction_statement)
    speechToUnity.say_something(introduction_statement, language_google, gender_google)
    while speechToUnity.is_speaking:
        time.sleep(0.1)
    
    time.sleep(4)
    
    # Avatar saying instruction  
    instruction_statement = text_strings['instruction']
    print(f"{avatar_name}:> {instruction_statement}")
    log_string(avatar_name, instruction_statement)
    speechToUnity.say_something(instruction_statement, language_google, gender_google)
    while speechToUnity.is_speaking:
        time.sleep(0.1)

    # Set conversational data
    end = False
    time_out: int = 0
    conversation_history = []

    while not end:
        # Wait for arbitrary answer from user
        result = speech_recognizer.recognize_once()
        transcript = result.text
        cleaned = transcript.strip().lower().rstrip(".,!?")
        print(f"{user_name}:> {transcript}")
        log_string(user_name, transcript)

        
        if cleaned == text_strings['ending'].lower():
            print("Ending word detected, stopping conversation.")
            speechToUnity.send_chat(user_name, transcript)
            break
        
        elif cleaned == text_strings['continue'].lower():
            print("Ja detected, giving instructions again...")
            speechToUnity.send_chat(user_name, transcript)
            response = text_strings['instruction']
            print(f"{avatar_name}:> {response}")
            log_string(avatar_name, response)
            speechToUnity.say_something(response, language_google, gender_google)
            while speechToUnity.is_speaking:
                time.sleep(0.1)
                
        elif transcript != "":
            time_out = 0
            speechToUnity.send_chat(user_name, transcript)
            ranked_results = rag_model.retrieve(transcript, top_k)
            context = rag_model.create_context(ranked_results)
            
            # Ask Mistral LLM
            response = ask_mistral(client, transcript, context, conversation_history, language, text_strings)
            print(f"{avatar_name}:> {response}")
            log_string(avatar_name, response)
            speechToUnity.say_something(response, language_google, gender_google)
            while speechToUnity.is_speaking:
                time.sleep(0.1)
                        
            # Update conversation history
            conversation_history.append({"role": "user", "content": transcript})
            conversation_history.append({"role": "assistant", "content": response})
            
            # Evaluate LLM answer
            top_chunks = [chunk for _, chunk, _ in ranked_results]
            metrics = rag_model.evaluate_llm_answer(transcript, response, top_chunks, rag_model.embedding_model)
            log_eval(metrics, transcript, response)
            
            # Ask follow up question
            question = random.choice(follow_up_questions)
            print(f"{avatar_name}:> {question}")
            log_string(avatar_name, question)
            speechToUnity.say_something(question, language_google, gender_google)
            while speechToUnity.is_speaking:
                time.sleep(0.1)
                
        elif transcript == "":
            log_string(user_name, "(silent)")
            speechToUnity.send_chat(user_name, "(silent)")
            time_out = time_out + 1
            #print("timeout = " + str(time_out))
            if time_out >= 10:
                print("Timeout limit reached, stopping conversation.")
                break

    # End conversation
    if time_out < 10:
        closing_statement = text_strings['you_are_welcome']
    else:
        closing_statement = text_strings['no_response_detected']
        
    print(f"{avatar_name}:> {closing_statement}")
    log_string(avatar_name, closing_statement)
    speechToUnity.send_chat(avatar_name, closing_statement)
    speechToUnity.say_something(closing_statement, language_google, gender_google)
    while speechToUnity.is_speaking:
        time.sleep(0.1)
        
    save_log_to_csv()
    print("Log saved.")

    return log_data