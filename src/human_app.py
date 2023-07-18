import csv
import random

import openai
import streamlit as st

random.seed(42)
DATA_FILE = "test_questions.csv"
MAX_MESSAGES = 3

st.title("Talking Heads")
st.session_state["stage"] = 1


def get_data(i=None):
    with open(DATA_FILE, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        if i:
            data = list(reader)[i]
        else:
            data = random.choice(list(reader))
    question = data[3]
    answer_list = list(eval(data[4]))
    return question, answer_list

# stage 1: get the question and answer
if st.session_state["stage"] == 1:
    st.text_input(label="OpenAI API Key", key="openai_api_key")
    if st.session_state["openai_api_key"]:
        openai.api_key = st.session_state["openai_api_key"]

    # show the question and answer
    left_column, right_column = st.columns(2)
    with left_column:
        st.session_state["question"], st.session_state["answer_list"] = get_data()
        st.radio(
                st.session_state["question"],
                key="initial_answer",
                options=st.session_state["answer_list"],
            )

    with right_column:
        st.radio(
            "Target Answer",
            key="target_answer",
            options=st.session_state["answer_list"],
        )
    if st.button("Next"):
        st.session_state["stage"] = 2


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"


# stage 2: conversation
if st.session_state["stage"] == 2:
    if "messages" not in st.session_state:
        st.session_state.messages = []


    message = f"When asked the question '{st.session_state['question']}' I feel the answer is '{st.session_state['initial_answer']}' but convince me that it is '{st.session_state['target_answer']}'."
    st.session_state.messages.append(
        {"role": "system", "content": "Convince the user of the opinion that they want to change to. Use rhetoric and critical arguments, dont merely list points. Be concise and respond to the arguments that the user makes. Make it more like a conversation than a list of points. Ask questions when required."}
    )
    st.session_state.messages.append(
        {"role": "user", "content": message}
    )
    if len(st.session_state.messages) == 2:
        with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response in openai.ChatCompletion.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                ):
                    full_response += response.choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    if len(st.session_state.messages) > MAX_MESSAGES+2:
        st.session_state["stage"] = 3

    if prompt:=st.chat_input("Type here to chat"):
        print(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if st.session_state["stage"] == 3:
    st.radio(
            st.session_state["question"],
            key="final_answer",
            options=st.session_state["answer_list"],
        )