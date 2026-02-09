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


def persona_card(p: dict) -> str:
    """Formaterer persona-info til visning."""
    themes = ", ".join(p["themes"])
    return (
        f"**{p['name']}** ({p['age']} år) — {p['context']}\n\n"
        f"{p['background_short']}\n\n"
        f"*Temaer: {themes}*"
    )


def show_sidebar():
    """Sidebar med persona-valg og indstillinger."""
    with st.sidebar:
        st.title("Indstillinger")

        # Persona-valg
        personas = PersonaEngine.list_personas()
        persona_names = [f"{p['name']} ({p['age']} år)" for p in personas]
        persona_ids = [p["id"] for p in personas]

        selected_idx = st.selectbox(
            "Vælg persona",
            range(len(personas)),
            format_func=lambda i: persona_names[i],
            key="persona_select",
        )
        selected_id = persona_ids[selected_idx]
        selected_persona = personas[selected_idx]

        # Vis persona-info
        st.markdown("---")
        st.markdown(f"**{selected_persona['context']}**")
        st.markdown(selected_persona["background_short"])
        st.markdown("**Temaer:**")
        for theme in selected_persona["themes"]:
            st.markdown(f"- {theme}")

        # Model-valg
        st.markdown("---")
        model = st.radio(
            "AI Model",
            ["sonnet", "opus"],
            format_func=lambda m: "Sonnet (hurtig, anbefalet)" if m == "sonnet" else "Opus (bedste kvalitet)",
            index=0,
        )

        thinking = st.toggle("Extended thinking", value=True, help="AI'en tænker før den svarer - giver mere nuancerede svar")

        # Ny samtale
        st.markdown("---")
        if st.button("Ny samtale", type="primary", use_container_width=True):
            st.session_state.pop("engine", None)
            st.session_state.pop("messages", None)
            st.session_state.pop("analysis", None)
            st.rerun()

        # Feedback-knap
        if st.button("Afslut og få feedback", use_container_width=True):
            st.session_state["show_analysis"] = True
            st.rerun()

        return selected_id, model, thinking


def get_engine(persona_id: str, model: str, thinking: bool) -> PersonaEngine:
    """Henter eller opretter engine i session state."""
    needs_new = (
        "engine" not in st.session_state
        or st.session_state.get("current_persona") != persona_id
        or st.session_state.get("current_model") != model
        or st.session_state.get("current_thinking") != thinking
    )

    if needs_new:
        st.session_state["engine"] = PersonaEngine(
            persona_id=persona_id,
            model=model,
            extended_thinking=thinking,
        )
        st.session_state["messages"] = []
        st.session_state["current_persona"] = persona_id
        st.session_state["current_model"] = model
        st.session_state["current_thinking"] = thinking
        st.session_state["analysis"] = None
        st.session_state["show_analysis"] = False

    return st.session_state["engine"]


def main():
    init_page()

    st.title("Persona Træningsplatform")
    st.caption("Social- og specialpædagogisk samtale-simulation med AI")

    persona_id, model, thinking = show_sidebar()
    engine = get_engine(persona_id, model, thinking)
    scenario = engine.get_scenario()

    # Vis scenario
    with st.container():
        st.info(
            f"**{scenario['setting']}**\n\n{scenario['intro']}",
            icon="📍",
        )

    # Vis samtalehistorik
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"] == "user" else "🧑"):
            st.markdown(msg["content"])
            if msg.get("thinking"):
                with st.expander("Vis tankeproces"):
                    st.markdown(msg["thinking"])

    # Feedback-sektion
    if st.session_state.get("show_analysis") and st.session_state["messages"]:
        st.markdown("---")
        st.subheader("Feedback på din kommunikation")

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
        # Vis brugerens besked
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)

        # Få svar
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
