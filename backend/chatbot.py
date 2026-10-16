# import streamlit as st
# from vector_DB import smart_response
# from vector_DB import agent_router
# from agent import run_agent


# # mémoire conversation
# if "history" not in st.session_state:
#     st.session_state.history = []

# st.title("🩺 AI Health Assistant")

# user_input = st.text_input("Ask a medical question:")

# if st.button("Send") and user_input:
    
#     # réponse AI
#     # response = smart_response(user_input)
#     # response = agent_router(user_input, st.session_state.history)
#     response = run_agent(user_input)

#     # ajouter historique
#     st.session_state.history.append(("You", user_input))
#     st.session_state.history.append(("Bot", response))

# # afficher conversation
# for speaker, text in st.session_state.history:
#     if speaker == "You":
#         st.markdown(f"**🧑 You:** {text}")
#     else:
#         st.markdown(f"**🤖 Bot:** {text}")

import streamlit as st
import requests

st.title("AI Health Assistant")

q = st.text_input("Ask:")

if st.button("Send"):
    res = requests.get("http://localhost:8000/ask", params={"question": q})
    st.write(res.json()["answer"])