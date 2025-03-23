import pandas as pd
import random
import streamlit as st

st.set_page_config(
    page_title="Paradigma Politico",
    page_icon="⚛️",
   layout="wide",
)


from streamlit.components.v1 import html
js_code = """
<script defer data-domain="paradigmapolitico.online" src="https://plausible.io/js/script.js"></script>
"""
html(js_code, height=100)


# TODO: Random generator for different distributions. Include random angle in a n-sphere.


st.header("Paradigma politico", divider="blue")
st.markdown("""
    Ola! Construimos este site com o intuito de te ajudar a perceber o teu alinhamento político.
    Far-lhe-emos várias perguntas, tentando perceber com qual partido e que a tua opinião se enquadra.
""")

political_parties = {
    "AD": "https://ad2024.pt/",
    "ADN": "https://adn.com.pt/",
    "BE": "https://www.bloco.org/",
    "Chega": "https://partidochega.pt/",
    "IL": "https://iniciativaliberal.pt/",
    "JPP": "https://juntospelopovo.pt/",
    "Livre": "https://partidolivre.pt/",
    "Nova Direita": "https://novadireita.pt/",
    "PAN": "https://pan-portugal.com/",
    "PCP": "https://www.pcp.pt/",
    "PCTP/MRPP": "???",
    "PS": "https://ps.pt/",
    "RIR": "https://partido-rir.pt/",
    "Volt": "https://voltportugal.org/",
}

st.markdown("Sites relevantes: " + "   |   ".join([f"[{text}]({url})" for text, url in political_parties.items()]))

if 'answers' not in st.session_state:
    st.session_state.answers = dict()

party_answers = pd.read_csv("paradigma_politico.csv")
party_answers.set_index("Pergunta", inplace=True)

# Take a random question
question = random.choice([
    q for q in party_answers.index
    if q not in st.session_state.answers.keys()
])

if 'previous_question' not in st.session_state:
    st.session_state.previous_question = question


gc1, gc2 = st.columns([7,3])

with gc1:
    st.header("Próxima Questão", divider="orange")

    st.markdown(question)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("Discordo totalmente"):
            st.session_state.answers[st.session_state.previous_question] = -2
    with c2:
        if st.button("Discordo parcialmente"):
            st.session_state.answers[st.session_state.previous_question] = -1
    with c3:
        if st.button("Posicao Neutra"):
            st.session_state.answers[st.session_state.previous_question] = -0
    with c4:
        if st.button("Concordo parcialmente"):
            st.session_state.answers[st.session_state.previous_question] = 1
    with c5:
        if st.button("Concordo totalmente"):
            st.session_state.answers[st.session_state.previous_question] = 2

with gc2:
    st.header("Semelhança política", divider="green")
    respostas_uteis = party_answers[party_answers.index.isin(st.session_state.answers.keys())]
    respostas_uteis["Utilizador"] = [st.session_state.answers[q] for q in respostas_uteis.index]
    for p in political_parties.keys():
        respostas_uteis[p] -= respostas_uteis["Utilizador"]
        respostas_uteis[p] = respostas_uteis[p]**2
    respostas_uteis.drop("Utilizador", axis=1, inplace=True)
    distances = respostas_uteis.sum(axis=0)
    distances = 1/(1+distances)
    distances /= (distances.max() / 100)

    distances.sort_values(ascending=False, inplace=True)
    distances.reindex()
    st.bar_chart(distances.sort_values(ascending=False))


st.header("Historico", divider="red")

# st.text(st.session_state)

st.caption("""
    Estas respostas são baseadas no conhecimento que os autores têm dos vários partidos.
    Caso exista alguma posição que deva ser alterada, podem [entrar em contacto](https://forms.gle/YV4eT6r1R5zaxrF28).
    Na lista abaixo, ✒️ representa o teu voto.
""")

for q in st.session_state.answers.keys():

    alignments = [
        ", ".join([
            p for p in political_parties.keys()
            if party_answers.loc[q, p] == v
        ])
        for v in range(-2, 3)
    ]
    index_to_be_updated = st.session_state.answers[q]+2
    alignments[index_to_be_updated] = "[✒️] " + alignments[index_to_be_updated]

    expander = st.expander(q)
    with expander:
        for c, text in zip(st.columns(5), alignments):
            with c:
                st.markdown(text)

st.session_state.previous_question = question
