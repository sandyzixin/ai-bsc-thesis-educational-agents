import streamlit as st
import os
import datetime
import re
import csv
import random
from mistralai.client import Mistral
import statements
import mistral_prompt
from RAG.rag import RAG

st.set_page_config(
    page_title="Japan Political System Tutor",
    page_icon="🇯🇵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.header('Japan Politics Tutor')

# logging
def log_string(speaker: str, spoken_text: str):
    current_time = datetime.datetime.now().isoformat(timespec="seconds")
    st.session_state.log_data.append((current_time, speaker, spoken_text))

def log_eval(metrics: dict, query: str, answer: str):
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    st.session_state.eval_data.append((
        timestamp,
        query,
        answer,
        metrics["answer_query_similarity"],
        metrics["answer_context_similarity"],
        metrics["overlap_count"],
        metrics["overlap_pct"]
    ))

def save_log_to_csv():
    os.makedirs("logs", exist_ok=True)
    # Dialogue log
    dialogue_file = f"logs/C_dialogue_{st.session_state.session_id}.csv"
    with open(dialogue_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["timestamp", "speaker", "text"])
        writer.writerows(st.session_state.log_data)

    # Eval log
    eval_file = f"logs/C_eval_{st.session_state.session_id}.csv"
    with open(eval_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["timestamp", "query", "answer", "query_similarity", "context_similarity", "overlap_count", "overlap_pct"])
        writer.writerows(st.session_state.eval_data)

# initialize experiment settings
language = st.session_state.get("language", "EN")
if language == "NL":
    text_strings = statements.nl_text_strings
    display_strings = statements.nl_display_text_strings
    follow_up_questions = statements.nl_follow_up_questions
elif language == "EN":
    text_strings = statements.en_text_strings
    display_strings = statements.en_display_text_strings
    follow_up_questions = statements.en_follow_up_questions

avatar_name = display_strings['Avatar']
user_name = display_strings['You']
top_k = 3

# session state
if "rag" not in st.session_state:
    with st.spinner("Loading knowledge base..."):
        document_path = "japan_politics.txt"
        embed_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        st.session_state.rag = RAG(document_path, embed_model)
        st.session_state.rag.preprocess()

if "client" not in st.session_state:
    my_api_key = st.secrets["MISTRAL_KEY"]
    st.session_state.client = Mistral(api_key=my_api_key)

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

if "log_data" not in st.session_state:
    st.session_state.log_data = []

if "eval_data" not in st.session_state:
    st.session_state.eval_data = []

if "ended" not in st.session_state:
    st.session_state.ended = False

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# show welcome message once
if len(st.session_state.log_data) == 0:
    log_string(avatar_name, text_strings['greeting'])
    log_string(avatar_name, text_strings['introduction'])

# display chat history
for _, speaker, text in st.session_state.log_data:
    if speaker == avatar_name:
        role = "assistant" 
    else:
        role = "user"
    with st.chat_message(role):
        st.write(text)

# User input
if not st.session_state.ended:
    if query := st.chat_input("Ask a question..."):
        log_string(user_name, query)
        st.session_state.conversation_history.append({"role": "user", "content": query})
        cleaned_query = query.strip().lower()
        if cleaned_query == text_strings['ending'].lower():
            closing = text_strings['you_are_welcome']
            log_string(avatar_name, closing)
            save_log_to_csv()
            st.session_state.ended = True
            #st.switch_page("pages/thank_you.py")
        elif cleaned_query == text_strings['continue'].lower():
            instruction = text_strings['instruction']
            log_string(avatar_name, instruction)
        else:
            st.session_state.pending_query = query
            
        st.rerun()

# Avatar output
if st.session_state.pending_query:
    ranked_results = st.session_state.rag.retrieve(st.session_state.pending_query, top_k)
    context = st.session_state.rag.create_context(ranked_results)
    with st.spinner("Thinking..."):
        response = mistral_prompt.ask_mistral(st.session_state.client, st.session_state.pending_query, context, st.session_state.conversation_history, language, text_strings)
    question = random.choice(follow_up_questions)
    log_string(avatar_name, response)
    log_string(avatar_name, question)
    
    st.session_state.conversation_history.append({"role": "chatbot", "content": response})
    
    # Evaluate LLM answer
    top_chunks = [chunk for _, chunk, _ in ranked_results]
    metrics = st.session_state.rag.evaluate_llm_answer(st.session_state.pending_query, response, top_chunks, st.session_state.rag.embedding_model)
    log_eval(metrics, st.session_state.pending_query, response)
    
    st.session_state.pending_query = None
    st.rerun()
