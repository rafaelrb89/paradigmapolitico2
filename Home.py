import pandas as pd
import streamlit as st
import altair as alt
import urllib.parse # Keep for sharing links

# -------------------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="Paradigma Politico",
    page_icon="⚛️",
    layout="wide",
)

# -------------------------------------------------------------------------
# **NEW**: Define App URL Placeholder (REPLACE THIS WHEN DEPLOYED)
# -------------------------------------------------------------------------
APP_URL = "https://paradigmapolitico2.streamlit.app/" # IMPORTANT: Replace this!

# -------------------------------------------------------------------------
# Custom Color Map for Affinity Chart
# -------------------------------------------------------------------------
party_color_map = {
    "PS": "#FF1493", "AD": "orange", "Livre": "#7FFF00", "PAN": "forestgreen",
    "IL": "cyan", "BE": "#FFC0CB", "CDU": "#EE0000", "Chega": "blue",
    "RIR": "yellow", "JPP": "#7FFFD4", "ADN": "darkgrey", "PCTP/MRPP": "#8B2323",
    "Nova Direita": "lightskyblue", "Volt": "purple",
}

# -------------------------------------------------------------------------
# CSS Styling (Attempting More Specific Selectors for Skip/Back)
# -------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* --- General Text & Background --- */
    body { background-color: #0E1117 !important; }
    .stApp { background-color: #0E1117 !important; }
    h1, h2, h3, h4, h5, h6, p, div, span, label, input, textarea, li { color: #FFFFFF !important; }
    a { color: #1E90FF !important; }

    /* --- Altair Chart Visibility --- */
    .vega-visualization { background-color: transparent !important; }
    .vega-visualization svg text { fill: #FFFFFF !important; font-size: 11px; }
    .vega-visualization svg .axis-title { font-size: 13px !important; fill: #E0E0E0 !important; }
    .vega-visualization svg .legend-title { font-size: 13px !important; fill: #E0E0E0 !important; }
    .vega-visualization svg .legend-label { fill: #CCCCCC !important; font-size: 11px !important; }
    .vega-visualization svg .axis path, .vega-visualization svg .axis line, .vega-visualization svg .axis .tick { stroke: #CCCCCC !important; }
    .vega-visualization svg .axis .domain { stroke-width: 1px; }
    .compass-text-label { fill: #FFFFFF !important; }

    /* --- Button Styling --- */
    /* Answer Buttons (Horizontal) - Keep As Is */
    div[data-testid="stHorizontalBlock"] button { width: 100%; color: #ffffff !important; border-radius: 4px; border: none;}
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) button { background-color: #8B0000 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) button { background-color: #FF6347 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(3) button { background-color: #FFD700 !important; color: #000000 !important;}
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(4) button { background-color: #556B2F !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(5) button { background-color: #006400 !important; }

    /* **MODIFIED**: Skip Button Styling (More Specific Selector) */
    .skip-btn-wrapper { margin-top: 15px !important; margin-bottom: 5px !important; }
    .skip-btn-wrapper div[data-testid="stButton"] button { /* More Specific */
        background-color: #555555 !important; /* Dark Grey */
        color: #ffffff !important; /* Force white text */
        width: 100% !important;
        padding: 0.5em 1em !important;
        font-weight: bold;
        border: none !important;
        border-radius: 4px;
    }

    /* **MODIFIED**: Back Button Styling (More Specific Selector) */
    .recuar-btn-wrapper { margin-top: 10px !important; margin-bottom: 10px !important; }
    .recuar-btn-wrapper div[data-testid="stButton"] button { /* More Specific */
        background-color: #777777 !important; /* Grey */
        color: #ffffff !important; /* Force white text */
        width: 100% !important;
        padding: 0.5em 1em !important;
        font-weight: bold;
        border: none !important;
        border-radius: 4px;
    }

    /* Start/Midpoint Button Styling - Keep As Is */
    .start-btn button, .midpoint-btn button { font-weight: bold !important; padding: 0.6em 1em !important; width: 100%; border-radius: 5px; border: none;}
    .start-btn button { background-color: #003300 !important; color: #ffffff !important; font-size: 1.1rem !important; }
    .midpoint-btn button { background-color: #003366 !important; color: #ffffff !important; font-size: 1.0rem !important; margin-top: 10px;}
    .start-btn-container { display: flex; justify-content: center; margin-top: 20px; gap: 20px;}

    /* Share Buttons - Keep As Is */
    .share-btn { display: inline-block; padding: 8px 15px; margin: 5px 3px; border-radius: 5px; color: white !important; text-decoration: none; font-weight: bold; text-align: center; border: none; cursor: pointer; }
    .share-btn:hover { opacity: 0.9; text-decoration: none; color: white !important; }
    .share-btn-facebook { background-color: #1877F2; }
    .share-btn-x { background-color: #1DA1F2; }
    .share-btn-whatsapp { background-color: #25D366; }
    .share-btn-email { background-color: #777777; }
    .share-button-container { text-align: center; margin-top: 20px;}

    /* Expander Styling - Keep As Is */
    .stExpander div[data-testid="stExpanderDetails"] { background-color: #222222; padding: 15px; border-radius: 5px; border: 1px solid #444444; }
    .stExpander div[data-testid="stExpanderDetails"] p, .stExpander div[data-testid="stExpanderDetails"] li, .stExpander div[data-testid="stExpanderDetails"] strong { color: #FFFFFF !important; }
    .stExpander div[data-testid="stExpanderDetails"] a { color: #90CAF9 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------------------
# Constants and Data Loading
# -------------------------------------------------------------------------
# (Code remains the same - assumes CSV loading handles 'Curto' column)
CSV_FILE = "paradigma_politico.csv"
NUM_ECONOMIC_QUESTIONS = 20
NUM_SOCIAL_QUESTIONS = 20
NUM_POLITICAL_QUESTIONS = 20
EXPECTED_TOTAL_QUESTIONS = NUM_ECONOMIC_QUESTIONS + NUM_SOCIAL_QUESTIONS + NUM_POLITICAL_QUESTIONS
SHORT_TEST_SIZE = 24

try:
    party_answers_df = pd.read_csv(CSV_FILE)
    required_cols = ["Pergunta", "Multiplicador", "Curto"]
    missing_req_cols = [col for col in required_cols if col not in party_answers_df.columns]
    if missing_req_cols:
        st.error(f"Erro: Coluna(s) necessária(s) não encontrada(s): {', '.join(missing_req_cols)}")
        st.stop()

    party_answers_df.set_index("Pergunta", inplace=True)
    multipliers = party_answers_df['Multiplicador']
    is_short_question_col = party_answers_df['Curto']

    if not multipliers.isin([1, -1]).all():
        st.warning("Atenção: 'Multiplicador' contém valores inválidos.")

    try:
        short_questions_indices = pd.to_numeric(is_short_question_col, errors='coerce') == 1
        short_questions_list = party_answers_df[short_questions_indices].index.tolist()
        if len(short_questions_list) != SHORT_TEST_SIZE:
            st.warning(f"Atenção: Encontradas {len(short_questions_list)} perguntas curtas, esperado {SHORT_TEST_SIZE}.")
        can_run_short_test = bool(short_questions_list)
        if not can_run_short_test:
            st.error("Erro: Nenhuma pergunta para teste curto (coluna 'Curto').")
    except Exception as e:
        st.error(f"Erro ao processar coluna 'Curto': {e}")
        short_questions_list = []
        can_run_short_test = False

    party_answers = party_answers_df.drop(columns=['Multiplicador', 'Curto'], errors='ignore')

except FileNotFoundError:
    st.error(f"Erro: Ficheiro '{CSV_FILE}' não encontrado.")
    st.stop()
except Exception as e:
    st.error(f"Erro ao ler ou processar CSV: {e}")
    st.stop()

questions = list(party_answers.index)
TOTAL_QUESTIONS_IN_FILE = len(questions)

if TOTAL_QUESTIONS_IN_FILE < EXPECTED_TOTAL_QUESTIONS:
    st.warning(f"Atenção: Ficheiro tem {TOTAL_QUESTIONS_IN_FILE} perguntas, esperado {EXPECTED_TOTAL_QUESTIONS}.")

# Define parties and URLs
defined_parties = {
    "AD": "https://ad2024.pt/",
    "ADN": "https://adn.com.pt/",
    "BE": "https://www.bloco.org/",
    "CDU": "https://www.pcp.pt/",
    "Chega": "https://partidochega.pt/",
    "IL": "https://iniciativaliberal.pt/",
    "JPP": "https://juntospelopovo.pt/",
    "Livre": "https://partidolivre.pt/",
    "Nova Direita": "https://novadireita.pt/",
    "PAN": "https://pan-portugal.com/",
    "PCTP/MRPP": "https://www.pctpmrpp.org/",
    "PS": "https://ps.pt/",
    "RIR": "https://partido-rir.pt/",
    "Volt": "https://voltportugal.org/",
}
valid_parties_in_csv = [p for p in defined_parties if p in party_answers.columns]
missing_parties = [p for p in defined_parties if p not in party_answers.columns]

if missing_parties:
    st.warning(f"Partidos definidos mas não encontrados no CSV: {', '.join(missing_parties)}")
if not valid_parties_in_csv:
    st.error("Erro: Nenhum partido definido encontrado no CSV.")
    st.stop()

party_answers = party_answers[valid_parties_in_csv]
political_parties = {p: url for p, url in defined_parties.items() if p in valid_parties_in_csv}
party_color_map = {p: color for p, color in party_color_map.items() if p in valid_parties_in_csv}
party_details = { # Assume populated as before
     "PS": {
         "fundacao": "19/04/1973",
         "descricao": "Centro-esquerda",
         "lider": "Pedro Nuno Santos",
         "programa_url": "https://ps.pt/programa/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Partido_Socialista_(Portugal)"},
     "AD": {
         "fundacao": "PPD/PSD: 06/05/1974",
         "descricao": "Centro-direita",
         "lider": "Luís Montenegro",
         "programa_url": "https://ad2024.pt/programa-eleitoral/",
         "wiki_url": "https://pt.wikipedia.org/wiki/AD_%E2%80%94_ALIAN%C3%87A_DEMOCR%C3%81TICA_(2024-Presente)"},
     "Livre": {
         "fundacao": "2014",
         "descricao": "Esquerda ecologista",
         "lider": "Rui Tavares e Isabel Mendes Lopes",
         "programa_url": "https://partidolivre.pt/programa",
         "wiki_url": "https://pt.wikipedia.org/wiki/Livre_(partido_pol%C3%ADtico)"},
     "PAN": {
         "fundacao": "2011",
         "descricao": "Ambientalista",
         "lider": "Inês Sousa Real",
         "programa_url": "https://pan-portugal.com/programas/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Pessoas%E2%80%93Animais%E2%80%93Natureza"},
     "IL": {
         "fundacao": "2017",
         "descricao": "Liberal",
         "lider": "Rui Rocha",
         "programa_url": "https://iniciativaliberal.pt/programa-politico/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Iniciativa_Liberal"},
     "BE": {
         "fundacao": "1999",
         "descricao": "Esquerda",
         "lider": "Mariana Mortágua",
         "programa_url": "https://www.bloco.org/programa",
         "wiki_url": "https://pt.wikipedia.org/wiki/Bloco_de_Esquerda"},
     "CDU": {
         "fundacao": "PCP: 1921",
         "descricao": "Coligação Comunista/Verdes",
         "lider": "Paulo Raimundo",
         "programa_url": "https://www.cdu.pt/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Coliga%C3%A7%C3%A3o_Democr%C3%A1tica_Unit%C3%A1ria"},
     "Chega": {
         "fundacao": "2019",
         "descricao": "Direita nacionalista/populista",
         "lider": "André Ventura",
         "programa_url": "https://partidochega.pt/programa/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Chega_(partido_pol%C3%ADtico)"},
     "RIR": {
         "fundacao": "2019",
         "descricao": "Centrista",
         "lider": "Márcia Henriques",
         "programa_url": "https://partido-rir.pt/ideias-e-programa/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Reagir_Incluir_Reciclar"},
     "JPP": {
         "fundacao": "2015",
         "descricao": "Regionalista (Madeira)",
         "lider": "Élvio Sousa, Filipe Sousa",
         "programa_url": "https://juntospelopovo.pt/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Juntos_pelo_Povo"},
     "ADN": {
         "fundacao": "2015/2021",
         "descricao": "Conservador nacionalista",
         "lider": "Bruno Fialho",
         "programa_url": "https://adn.com.pt/programa-eleitoral/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Alternativa_Democr%C3%A1tica_Nacional"},
     "PCTP/MRPP": {
         "fundacao": "1970/1976",
         "descricao": "Comunista (ML)",
         "lider": "N/A",
         "programa_url": "https://www.pctpmrpp.org/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Partido_Comunista_dos_Trabalhadores_Portugueses"},
     "Nova Direita": {
         "fundacao": "2023",
         "descricao": "Conservador liberal",
         "lider": "Ossanda Liber",
         "programa_url": "https://novadireita.pt/manifesto/",
         "wiki_url": "https://pt.wikipedia.org/wiki/Nova_Direita_(Portugal)"},
     "Volt": {
         "fundacao": "2020",
         "descricao": "Pan-europeu progressista",
         "lider": "Duarte Costa e Inês Bravo Figueiredo",
         "programa_url": "https://voltportugal.org/programa",
         "wiki_url": "https://pt.wikipedia.org/wiki/Volt_Portugal"
     }
 }
party_details = {p: details for p, details in party_details.items() if p in valid_parties_in_csv}

if 'mode' not in st.session_state:
    st.session_state.mode = 'intro'
if 'idx' not in st.session_state:
    st.session_state.idx = -1
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------

def show_intro():
    """Shows the intro page with test length choice."""

    # Use len(short_questions_list) if available, else SHORT_TEST_SIZE as fallback text
    short_q_count = len(short_questions_list) if can_run_short_test else SHORT_TEST_SIZE

    st.title("Paradigma Político")
    st.write(f"""
        Bem-vindo! Este teste visa **avaliar o seu posicionamento político**. O teste compara também o seu posicionamento em relação aos partidos portugueses que tiveram mais do que 7000 votos nas eleições legislativas de 2024 (mínimo de assinaturas para a formação de um partido político em Portugal).
        Em cada pergunta, o utilizador será confrontado com uma afirmação e será pedido para escolher qual o nível de concordância. As perguntas visam avaliar a posição relativamente a valores políticos abstractos e intemporais, não a questões especificas da realidade portuguesa num determinado ponto no tempo.
        O teste completo é composto por **60 perguntas** (20 perguntas por eixo). A descrição de cada um destes eixos é a seguinte:
        
        **Eixo Económico**: Mede o grau de intervenção geral do Estado na Economia.
        **Eixo Social**: Mede o grau de abertura a mudanças sociais.
        **Eixo Político**: Mede o grau de liberalismo político.
        
        Os resultados do teste mostram o posicionamento relativamente aos vários partidos políticos portugueses nos 3 eixos através de um mapa com 3 dimensões.
        Finalmente, o teste mostra ao grau de semelhança das resposta do utilzador em relação a cada partido, medido pela soma dos desvios absolutos em todas as respostas do teste.
        
        Pode optar por fazer um teste **curto de {short_q_count} perguntas** (resultados mais rápidos mas menos precisos) ou o teste **completo de {len(questions)} perguntas** (resultados mais fiáveis).
        ---
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='start-btn'>", unsafe_allow_html=True)
        if st.button(f"Iniciar Teste Curto ({short_q_count} Perguntas)", key="start_short", disabled=not can_run_short_test):
            st.session_state.mode = 'short'
            st.session_state.idx = 0
            st.session_state.answers = {}
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        if not can_run_short_test:
            st.caption("Opção indisponível.")
    with col2:
        st.markdown("<div class='start-btn'>", unsafe_allow_html=True)
        if st.button(f"Iniciar Teste Completo ({len(questions)} Perguntas)", key="start_full"):
            st.session_state.mode = 'full'
            st.session_state.idx = 0
            st.session_state.answers = {}
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("**Partidos incluídos:** " + " | ".join([f"[{p}]({url})" for p, url in political_parties.items()]))
    st.write("As respostas dos partidos são baseadas na avaliação da equipa que elaborou o teste tendo em conta os conteúdos dos mais recententes programas, posições públicas passadas, e a ideologia de cada partido. A equipa encontra-se disponível para ajustar as respostas de cada partido, caso os partidos entrem em contacto.")

def show_question(current_idx, question_list, total_questions_in_mode):
    """Shows the current question, answer buttons, skip, and back buttons."""
    if not (0 <= current_idx < len(question_list)):
        st.error("Erro interno: Índice de pergunta inválido.")
        st.session_state.mode = 'intro'
        st.session_state.idx = -1
        st.rerun()

    question_text = question_list[current_idx]
    st.header(f"Pergunta {current_idx + 1} de {total_questions_in_mode}")
    st.subheader(question_text)
    st.write("Qual a sua posição sobre esta afirmação?")

    # Define options, with "Neutro" renamed
    options = {
        "Discordo totalmente": -2,
        "Discordo parcialmente": -1,
        "Neutro ou Ambíguo": 0,
        "Concordo parcialmente": 1,
        "Concordo totalmente": 2
    }
    button_pressed_type = None
    next_idx = current_idx + 1

     # --- Answer Buttons ---
    cols = st.columns(5)
    for i, (label, value) in enumerate(options.items()):
        with cols[i]:
            # Use unique key combining question index and option index
            if st.button(label, key=f"q{current_idx}_opt_{i}"):
                st.session_state.answers[question_text] = value # Store answer
                st.session_state.idx = next_idx
                button_pressed_type = 'answer'
                break # Exit loop

    # Use a container for the full-width buttons below
    button_below_container = st.container()
    with button_below_container:
        # --- Skip Button (Full Width with Wrapper Class) ---
        # **MODIFIED**: Add wrapper div with class
        st.markdown("<div class='skip-btn-wrapper'>", unsafe_allow_html=True)
        if st.button("Sem opinião", key=f"q{current_idx}_skip", use_container_width=True):
            st.session_state.answers.pop(question_text, None)
            st.session_state.idx = next_idx
            button_pressed_type = 'skip'
        st.markdown("</div>", unsafe_allow_html=True) # Close wrapper

        # --- Back Button (Full Width with Wrapper Class, only if not first question) ---
        if current_idx > 0:
            # **MODIFIED**: Add wrapper div with class
            st.markdown("<div class='recuar-btn-wrapper'>", unsafe_allow_html=True)
            if st.button("Recuar", key=f"q{current_idx}_back", use_container_width=True):
                st.session_state.idx -= 1
                button_pressed_type = 'back'
            st.markdown("</div>", unsafe_allow_html=True) # Close wrapper


    # --- State Transition Logic ---
    # Needs to run *after* potentially setting button_pressed_type
    if button_pressed_type in ['answer', 'skip']:
        # Check if short test just finished
        if st.session_state.mode == 'short' and st.session_state.idx == len(short_questions_list):
            st.session_state.mode = 'midpoint'
            st.rerun()
        # Check if full test just finished
        elif st.session_state.mode == 'full' and st.session_state.idx == len(questions):
             st.session_state.mode = 'results'
             st.rerun()
        # Otherwise, just continue to next question if state didn't change above
        elif st.session_state.mode not in ['midpoint', 'results']:
             st.rerun()
    elif button_pressed_type == 'back':
         st.rerun() # Rerun if only back was pressed


def show_midpoint_choice():
    """Displays screen after short test, asking user to continue or see results."""
    st.header(f"Teste Curto ({len(short_questions_list)} Perguntas) Concluído!")
    st.write("Pode ver já os seus resultados (baseados nestas perguntas, menos precisos) ou continuar o teste para responder a todas as perguntas e obter resultados mais fiáveis.")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
         st.markdown("<div class='midpoint-btn'>", unsafe_allow_html=True)
         if st.button(f"Ver Resultados ({len(short_questions_list)} Perguntas)", key="results_short"):
              st.session_state.mode = 'results'
              st.rerun()
         st.markdown("</div>", unsafe_allow_html=True)
    with col2:
         st.markdown("<div class='midpoint-btn'>", unsafe_allow_html=True)
         if st.button(f"Continuar Teste ({len(questions)} Perguntas)", key="continue_full"):
              st.session_state.mode = 'full'
              st.rerun()
         st.markdown("</div>", unsafe_allow_html=True)


# (calculate_compass_scores remains unchanged)
def calculate_compass_scores(entity_answers, all_questions_list, question_multipliers):
    """ Calculates Economic, Social, and Political scores (-1 to 1) using multipliers. """
    scores = {
        'Economic': 0.0,
        'Political': 0.0,
        'Social': 0.0,
    }
    econ_end = min(len(all_questions_list), NUM_ECONOMIC_QUESTIONS)
    social_end = min(len(all_questions_list), NUM_ECONOMIC_QUESTIONS + NUM_SOCIAL_QUESTIONS)
    political_end = min(len(all_questions_list), EXPECTED_TOTAL_QUESTIONS)
    axis_definitions = {
        'Economic': all_questions_list[0:econ_end],
        'Political': all_questions_list[NUM_ECONOMIC_QUESTIONS + NUM_SOCIAL_QUESTIONS : political_end],
        'Social': all_questions_list[NUM_ECONOMIC_QUESTIONS:social_end],
    }
    for axis_name, question_texts in axis_definitions.items():
        if question_texts:
            valid_answers = entity_answers.reindex(question_texts).dropna()
            num_answered = len(valid_answers)
            if num_answered > 0:
                relevant_multipliers = question_multipliers.reindex(valid_answers.index)
                weighted_score_sum = (valid_answers * relevant_multipliers).sum()
                normalized_score = weighted_score_sum / (num_answered * 2.0)
                scores[axis_name] = max(-1.0, min(1.0, normalized_score))
    return scores['Economic'], scores['Social'], scores['Political']


def show_results():
    """Shows the results page: affinity chart, compass chart, party info, share buttons."""
    st.success("Teste concluído!")
    perguntas_respondidas_list = list(st.session_state.answers.keys())
    num_perguntas_respondidas = len(perguntas_respondidas_list)

    if not perguntas_respondidas_list:
        st.warning("Não respondeu a nenhuma pergunta.")
        if st.button("Reiniciar Teste"):
            st.session_state.mode = 'intro'
            st.session_state.idx = -1
            st.session_state.answers = {}; st.rerun()
        return

    # Add note about test length
    is_short_result = can_run_short_test and (num_perguntas_respondidas == len(short_questions_list)) and (len(short_questions_list) < len(questions))
    is_full_result = (num_perguntas_respondidas == len(questions))
    if is_short_result :
        st.info(f"Resultados baseados no teste curto de {num_perguntas_respondidas} perguntas.")
    elif is_full_result:
        st.info(f"Resultados baseados no teste completo de {num_perguntas_respondidas} perguntas.")
    else:
        st.info(f"Resultados baseados em {num_perguntas_respondidas} perguntas respondidas.")


    # --- 1. Affinity Score Calculation & Chart ---
    st.header("Percentagem de Concordância com os Partidos Portugueses")
    respostas_partidos_filtradas = party_answers.loc[perguntas_respondidas_list]
    user_answers_series = pd.Series(st.session_state.answers).reindex(perguntas_respondidas_list)
    total_distances = {}
    for party_name in political_parties.keys():
        if party_name in respostas_partidos_filtradas.columns:
            diff = abs(respostas_partidos_filtradas[party_name] - user_answers_series)
            total_distances[party_name] = diff.sum()
    total_distances_series = pd.Series(total_distances)
    max_dist = 4 * num_perguntas_respondidas if num_perguntas_respondidas > 0 else 1
    affinity = (1 - (total_distances_series / max_dist)).clip(lower=0.0, upper=1.0)
    affinity.sort_values(ascending=False, inplace=True)
    affinity_df = affinity.reset_index()
    affinity_df.columns = ['Partido', 'Concordância']
    color_domain = affinity_df['Partido'].tolist()
    color_range = [party_color_map.get(p, "#CCCCCC") for p in color_domain]
    affinity_chart = alt.Chart(affinity_df).mark_bar().encode(
        x=alt.X('Concordância', axis=alt.Axis(format='%', title="Percentagem de Concordância", grid=False)),
        y=alt.Y('Partido', sort='-x', title="Partido", axis=alt.Axis(labelLimit=200)),
        color=alt.Color('Partido', scale=alt.Scale(domain=color_domain, range=color_range), legend=None),
        tooltip=['Partido', alt.Tooltip('Concordância', format='.1%')]
    ).properties(
        background='transparent' # Add this line
    )
    st.altair_chart(affinity_chart, use_container_width=True)
    st.write("O gráfico acima mostra a concordância geral com base em todas as suas respostas. Quanto mais distante a resposta do utilizador da resposta de um determinado partido, menor o grau de semelhança. Um resultado de 100% indica uma concordância total com um determinado partido em todas as perguntas.")
    st.write("---")

    # --- 2. Political Compass Calculation & Chart (Yellow Liberal) ---
    st.header("Bússola Política")
    compass_data = []
    full_user_answers_series = pd.Series(st.session_state.answers)
    user_econ, user_social, user_political = calculate_compass_scores(full_user_answers_series, questions, multipliers)
    compass_data.append({"Entidade": "Você", "Eixo Económico": user_econ, "Eixo Social": user_social, "Eixo Político": user_political})
    for party_name in political_parties.keys():
        if party_name in party_answers.columns:
            party_col_full = party_answers[party_name]
            p_econ, p_social, p_political = calculate_compass_scores(party_col_full, questions, multipliers)
            compass_data.append({"Entidade": party_name, "Eixo Económico": p_econ, "Eixo Social": p_social, "Eixo Político": p_political})
    compass_df = pd.DataFrame(compass_data)

    if not compass_df.empty:
        origin_lines = pd.DataFrame({'zero': [0]})
        vline = alt.Chart(origin_lines).mark_rule(strokeDash=[3,3], color='grey', size=0.5).encode(x='zero:Q')
        hline = alt.Chart(origin_lines).mark_rule(strokeDash=[3,3], color='grey', size=0.5).encode(y='zero:Q')
        base = alt.Chart(compass_df).encode(
            x=alt.X('Eixo Económico', scale=alt.Scale(domain=[-1.1, 1.1]), axis=alt.Axis(title='Económico (Esquerda <-> Direita)', grid=False, format=".1f")),
            y=alt.Y('Eixo Social', scale=alt.Scale(domain=[-1.1, 1.1]), axis=alt.Axis(title='Social (Conservador <-> Progressista)', grid=False, format=".1f"))
        )
        # **MODIFIED**: Color scale range changed to Red-Grey-Yellow
        color_scale = alt.Scale(domain=[-1, 0, 1], range=['#FF0000', '#808080', '#FFFF00']) # Red, Grey, Yellow
        points = base.mark_point(size=100, filled=True, opacity=0.9).encode(
            color=alt.Color('Eixo Político', scale=color_scale, legend=alt.Legend(title="Eixo Político", orient="top", titleOrient="left", gradientLength=200, format=".1f")),
            tooltip=['Entidade', alt.Tooltip('Eixo Económico', format='.2f'), alt.Tooltip('Eixo Social', format='.2f'), alt.Tooltip('Eixo Político', format='.2f', title="Político (Aut/Lib)")],
            shape=alt.condition(alt.datum.Entidade == 'Você', alt.value('diamond'), alt.value('circle'))
        )
        text = base.mark_text(align='left', baseline='middle', dx=9, fontSize=12, fontWeight='bold').encode(text='Entidade', color=alt.value('#FFFFFF'))
        compass_chart = (vline + hline + points + text).properties(
            background='transparent'
        ).interactive()
        st.altair_chart(compass_chart, use_container_width=True)
        st.write(
             """
            **Como interpretar a Bússola Política:**
            * **Posição Horizontal (Eixo X):** Eixo **Económico**. Esquerda (-1) vs Direita (+1).
            * **Posição Vertical (Eixo Y):** Eixo **Social**. Conservador (-1) vs Progressista (+1).
            * **Côr:** Eixo **Político**. Vermelho (Autoritário, -1) -> Cinzento (Neutro, 0) -> Amarelo (Liberal, +1).

            A sua posição ("Você") é marcada com um losango (♦). As posições são calculadas com base nas respostas.
            """ # Updated explanation for marker and overlap acknowledgement
        )
        st.caption("Nota: Se as etiquetas se sobrepuserem, use o zoom ou passe o rato.")
    else:
        st.warning("Não foi possível gerar a Bússola Política.")
        st.write("---")

    # --- 3. Expandable Party Information Section ---
    st.subheader("Descobre mais sobre os Partidos")
    # (Party details expander loop remains the same)
    sorted_party_names = sorted(political_parties.keys())
    for party_name in sorted_party_names:
        with st.expander(f"{party_name}"):
            details = party_details.get(party_name, {})
            official_url = political_parties.get(party_name, "#")
            st.markdown(f"**Líder(es):** {details.get('lider', 'N/D')}")
            st.markdown(f"**Fundação:** {details.get('fundacao', 'N/D')}")
            st.markdown(f"**Descrição:** {details.get('descricao', 'N/D')}")
            st.markdown(f"**Links:** - [Site Oficial]({official_url})")
            programa_url = details.get('programa_url', '#')
            if programa_url.startswith("URL_") or programa_url == '#':
                programa_text = f"[Programa (Ver site)]({official_url})"
            elif programa_url:
                programa_text = f"[Programa]({programa_url})"
            else:
                programa_text = "Programa (Link N/D)"
            st.markdown(f"- {programa_text} - [Wikipedia]({details.get('wiki_url', '#')})")

    # --- 4. Share Results Section (Moved to End, No Insta/TikTok) ---
    st.write("---") # Separator before sharing
    st.subheader("Partilhar Resultados")

    # Generate summary text
    top_party = affinity_df.iloc[0]['Partido'] if not affinity_df.empty else "Nenhum"
    top_affinity = affinity_df.iloc[0]['Concordância'] if not affinity_df.empty else 0
    share_text_base = f"Fiz o teste Paradigma Político! O meu partido mais próximo foi {top_party} ({top_affinity:.0%}). Descobre a tua posição:"
    share_text_encoded = urllib.parse.quote_plus(f"{share_text_base} {APP_URL}")
    share_text_twitter = urllib.parse.quote_plus(f"{share_text_base}")
    app_url_encoded = urllib.parse.quote_plus(APP_URL)
    hashtags = "ParadigmaPoliticoPT,PoliticaPortuguesa"

    # Construct Share URLs
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={app_url_encoded}"
    x_url = f"https://twitter.com/intent/tweet?url={app_url_encoded}&text={share_text_twitter}&hashtags={hashtags}"
    whatsapp_url = f"https://wa.me/?text={share_text_encoded}"
    email_subject = urllib.parse.quote_plus("O meu resultado no Paradigma Político")
    email_url = f"mailto:?subject={email_subject}&body={share_text_encoded}"

    # Display Share Buttons/Links in a centered container
    st.markdown("<div class='share-button-container'>", unsafe_allow_html=True)
    st.markdown(f'<a href="{facebook_url}" target="_blank" class="share-btn share-btn-facebook">Facebook</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{x_url}" target="_blank" class="share-btn share-btn-x">X (Twitter)</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="share-btn share-btn-whatsapp">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{email_url}" target="_blank" class="share-btn share-btn-email">Email</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


    # --- Footer / Restart Button ---
    st.write("---")
    if st.button("Reiniciar Teste"):
        st.session_state.mode = 'intro'
        st.session_state.idx = -1
        st.session_state.answers = {}
        st.rerun()

# -------------------------------------------------------------------------
# Main Application Flow (Using Mode State)
# -------------------------------------------------------------------------
# (Main flow logic remains the same)
current_mode = st.session_state.get('mode', 'intro')

match current_mode:
    case 'intro':
        show_intro()
    case 'short':
        # Use length of actual short list for total
        show_question(st.session_state.idx, short_questions_list, len(short_questions_list))
    case 'full':
        total_q_display = len(questions)
        show_question(st.session_state.idx, questions, total_q_display)
    case 'midpoint':
        show_midpoint_choice()
    case 'results':
        show_results()
    case _: # Fallback
        st.error("Erro: Estado inválido. A reiniciar.")
        st.session_state.mode = 'intro'
        st.session_state.idx = -1
        st.session_state.answers = {}
        st.rerun()