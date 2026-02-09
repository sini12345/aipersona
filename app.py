"""
Streamlit Web App: Persona Træningsplatform
Social- og specialpædagogisk samtale-simulation

Kør med: streamlit run app.py
"""

import streamlit as st
from persona_engine import PersonaEngine


def init_page():
    st.set_page_config(
        page_title="Persona Træning",
        page_icon="🎓",
        layout="wide",
    )


def show_sidebar():
    """Sidebar med persona-valg, teori-valg og indstillinger."""
    with st.sidebar:
        st.title("Indstillinger")

        # --- 1. Persona-valg ---
        st.subheader("1. Vælg persona")
        personas = PersonaEngine.list_personas()
        persona_names = [f"{p['name']} ({p['age']} år)" for p in personas]
        persona_ids = [p["id"] for p in personas]

        selected_idx = st.selectbox(
            "Hvem vil du tale med?",
            range(len(personas)),
            format_func=lambda i: persona_names[i],
            key="persona_select",
        )
        selected_id = persona_ids[selected_idx]
        selected_persona = personas[selected_idx]

        st.caption(f"**{selected_persona['context']}**")
        st.caption(selected_persona["background_short"])

        # --- 2. Teori-valg ---
        st.markdown("---")
        st.subheader("2. Vælg teori (valgfri)")

        theories = PersonaEngine.list_theories()
        theory_options = ["Ingen teori valgt"] + [t["name"] for t in theories]
        theory_ids = [None] + [t["id"] for t in theories]

        theory_idx = st.selectbox(
            "Hvilken teori vil du træne?",
            range(len(theory_options)),
            format_func=lambda i: theory_options[i],
            key="theory_select",
        )
        selected_theory_id = theory_ids[theory_idx]

        if selected_theory_id:
            selected_theory = theories[theory_idx - 1]
            st.caption(f"*{selected_theory['authors']}*")
            with st.expander("Læs om teorien"):
                st.markdown(selected_theory["summary"])

        # --- 3. Tekst-upload ---
        st.markdown("---")
        st.subheader("3. Upload tekst (valgfri)")
        uploaded_file = st.file_uploader(
            "Upload pensum-tekst (.txt eller .pdf)",
            type=["txt", "pdf"],
            help="Teksten bruges som ekstra grundlag i feedbacken efter samtalen",
        )

        custom_text = None
        if uploaded_file is not None:
            if uploaded_file.type == "text/plain":
                custom_text = uploaded_file.read().decode("utf-8")
                st.success(f"Tekst indlæst ({len(custom_text):,} tegn)")
            elif uploaded_file.type == "application/pdf":
                try:
                    import pypdf
                    reader = pypdf.PdfReader(uploaded_file)
                    custom_text = "\n".join(
                        page.extract_text() or "" for page in reader.pages
                    )
                    st.success(f"PDF indlæst ({len(reader.pages)} sider, {len(custom_text):,} tegn)")
                except ImportError:
                    st.warning("Installer pypdf for PDF-support: `pip install pypdf`")
                except Exception as e:
                    st.error(f"Kunne ikke læse PDF: {e}")

        # --- 4. Model-valg ---
        st.markdown("---")
        st.subheader("4. Model")
        model = st.radio(
            "AI Model",
            ["sonnet", "opus"],
            format_func=lambda m: "Sonnet (anbefalet)" if m == "sonnet" else "Opus (bedste kvalitet)",
            index=0,
        )
        thinking = st.toggle("Extended thinking", value=True)

        # --- Knapper ---
        st.markdown("---")
        if st.button("Ny samtale", type="primary", use_container_width=True):
            for key in ["engine", "messages", "analysis", "show_analysis"]:
                st.session_state.pop(key, None)
            st.rerun()

        if st.button("Afslut og få feedback", use_container_width=True):
            st.session_state["show_analysis"] = True
            st.rerun()

        return selected_id, selected_theory_id, custom_text, model, thinking


def get_engine(
    persona_id: str,
    theory_id: str | None,
    custom_text: str | None,
    model: str,
    thinking: bool,
) -> PersonaEngine:
    """Henter eller opretter engine i session state."""
    needs_new = (
        "engine" not in st.session_state
        or st.session_state.get("current_persona") != persona_id
        or st.session_state.get("current_theory") != theory_id
        or st.session_state.get("current_model") != model
        or st.session_state.get("current_thinking") != thinking
    )

    if needs_new:
        st.session_state["engine"] = PersonaEngine(
            persona_id=persona_id,
            theory_id=theory_id,
            custom_theory_text=custom_text,
            model=model,
            extended_thinking=thinking,
        )
        st.session_state["messages"] = []
        st.session_state["current_persona"] = persona_id
        st.session_state["current_theory"] = theory_id
        st.session_state["current_model"] = model
        st.session_state["current_thinking"] = thinking
        st.session_state["analysis"] = None
        st.session_state["show_analysis"] = False

    return st.session_state["engine"]


def main():
    init_page()

    st.title("Persona Træningsplatform")
    st.caption("Social- og specialpædagogisk samtale-simulation med AI")

    persona_id, theory_id, custom_text, model, thinking = show_sidebar()
    engine = get_engine(persona_id, theory_id, custom_text, model, thinking)
    scenario = engine.get_scenario()

    # Header med persona + teori info
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info(
            f"**{scenario['setting']}**\n\n{scenario['intro']}",
            icon="📍",
        )
    with col2:
        if engine.theory:
            st.success(
                f"**Teori: {engine.theory['name']}**\n\n"
                f"*{engine.theory['authors']}*",
                icon="📚",
            )
        else:
            st.warning("Ingen teori valgt.\n\nFeedback baseres kun på persona-kriterier.", icon="📝")

    # Samtalehistorik
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        avatar = "🧑‍🎓" if msg["role"] == "user" else "🧑"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("thinking"):
                with st.expander("Vis tankeproces"):
                    st.markdown(msg["thinking"])

    # Feedback-sektion
    if st.session_state.get("show_analysis") and st.session_state.get("messages"):
        st.markdown("---")
        st.subheader("Feedback på din kommunikation")

        feedback_basis = [f"**Persona:** {engine.persona['name']}"]
        if engine.theory:
            feedback_basis.append(f"**Teori:** {engine.theory['name']}")
        if engine.custom_theory_text:
            feedback_basis.append("**Uploadet tekst:** Ja")
        st.caption(" | ".join(feedback_basis))

        if st.session_state.get("analysis") is None:
            with st.spinner("Analyserer din samtale..."):
                st.session_state["analysis"] = engine.analyze_student()

        st.markdown(st.session_state["analysis"])

        cost = engine.estimate_cost()
        st.caption(
            f"Session: {len(engine.session_stats['interactions'])} interaktioner | "
            f"{cost['total_tokens']:,} tokens | ~{cost['cost_dkk']} DKK"
        )
        return

    # Chat input
    if prompt := st.chat_input(f"Skriv til {engine.persona['name']}..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🧑"):
            with st.spinner(f"{engine.persona['name']} tænker..."):
                result = engine.chat(prompt)

            if "error" in result:
                st.error(f"Fejl: {result['error']}")
            else:
                st.markdown(result["response"])
                if result["thinking"]:
                    with st.expander("Vis tankeproces"):
                        st.markdown(result["thinking"])

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": result["response"],
                    "thinking": result.get("thinking"),
                })


if __name__ == "__main__":
    main()
