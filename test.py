import streamlit as st
import nltk
from nltk.chat.util import Chat, reflections
import speech_recognition as sr

# Téléchargez les données nécessaires pour nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Fonction pour charger les paires depuis un fichier
def load_pairs_from_file(filename):
    pairs = []
    with open(filename, 'r', encoding='utf-8') as file:
        current_q = None
        for line in file:
            line = line.strip()
            if line.startswith('Q:'):
                current_q = line[3:].strip()
            elif line.startswith('R:') and current_q:
                response = line[3:].strip()
                pairs.append([current_q, [response]])
                current_q = None
            elif line.startswith('- ') and current_q and pairs and pairs[-1][0] == current_q:
                pairs[-1][1].append(line[2:].strip())
    return pairs

# Charger les paires depuis le fichier
pairs = load_pairs_from_file('pairs.txt')

# Initialiser le chatbot
def chatbot_response(input_text):
    chat = Chat(pairs, reflections)
    response = chat.respond(input_text)
    return response if response else "Je ne comprends pas votre question. Pouvez-vous reformuler ?"

# Fonction pour transcrire la parole en texte
def transcribe_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Parlez maintenant...")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            text = r.recognize_google(audio, language="fr-FR")
            return text
        except sr.UnknownValueError:
            st.warning("🔇 Impossible de comprendre la parole. Veuillez réessayer.")
            return ""
        except sr.RequestError as e:
            st.error(f"⚠️ Erreur lors de la requête : {str(e)}")
            return ""
        except sr.WaitTimeoutError:
            st.warning("⏳ Temps écoulé. Veuillez parler plus rapidement.")
            return ""

# Application Streamlit améliorée
def main():
    st.title("🤖 ChatBot Expert en Data Science")
    st.write("Posez vos questions par écrit ou par voix")

    # Initialiser l'historique des messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Afficher l'historique des messages avec st.chat_message
    for msg in st.session_state.messages:
        role, text = msg.split(":", 1)
        with st.chat_message(role.strip()):
            st.write(text.strip())

    col1, col2 = st.columns([3, 1])

    with col1:
        user_input = st.text_input("💬 Tapez votre question ici :", "")

    with col2:
        if st.button("🎙️ Parler"):
            speech_text = transcribe_speech()
            if speech_text:
                st.session_state.messages.append(f"user: {speech_text}")
                response = chatbot_response(speech_text)
                st.session_state.messages.append(f"assistant: {response}")
                st.rerun()

    if st.button("📩 Envoyer") and user_input:
        st.session_state.messages.append(f"user: {user_input}")
        response = chatbot_response(user_input)
        st.session_state.messages.append(f"assistant: {response}")
        st.rerun()

    if st.button("🔄 Réinitialiser la conversation"):
        st.session_state.messages = []
        st.rerun()

if __name__ == "__main__":
    main()
