import os
import requests
import streamlit as st

st.set_page_config(page_title="Enterprise Analytics Copilot", layout="wide")
st.title("Enterprise Analytics Copilot")
st.caption("NL2SQL → validation → execution → analytical reasoning → business answer")

api_url = st.sidebar.text_input("API URL", os.getenv("API_URL", "http://localhost:8000/api"))
question = st.text_area(
    "Ask an analytics question",
    "Which stores have the highest sales?",
    height=100,
)

if st.button("Run analysis", type="primary"):
    try:
        r = requests.post(
            f"{api_url}/query",
            json={"question": question, "include_sql": True},
            timeout=90,
        )
        if r.ok:
            data = r.json()
            st.subheader("Business answer")
            st.write(data["answer"])

            if data.get("analysis"):
                st.subheader("Analytical reasoning")
                st.info(
                    f"Intent: {data['analysis']['intent']}\n\n"
                    f"Assumption: {data['analysis']['assumption']}"
                )
                with st.expander("Analysis steps", expanded=False):
                    for step in data["analysis"]["steps"]:
                        st.markdown(f"**{step['name']}** — {step['purpose']}")
                        st.code(step["sql"], language="sql")

            st.subheader("Generated SQL")
            st.code(data["sql"] or "No single SQL statement; multi-step analytical plan used.", language="sql")

            if data["rows"]:
                st.subheader("Result")
                st.dataframe(
                    [dict(zip(data["columns"], row)) for row in data["rows"]],
                    use_container_width=True,
                )

            if data.get("analysis"):
                with st.expander("Analytical step results", expanded=True):
                    for name, result in data["analysis"]["results"].items():
                        st.markdown(f"**{name}**")
                        if result["rows"]:
                            st.dataframe(
                                [dict(zip(result["columns"], row)) for row in result["rows"]],
                                use_container_width=True,
                            )

            st.subheader("Observability")
            st.json(data["metrics"])
            with st.expander("Agent trace"):
                st.json(data["trace"])
            with st.expander("Retrieved schema context"):
                st.json(data.get("schema_items", []))
        else:
            try:
                detail = r.json().get("detail", {})
                st.error(detail.get("answer", "The analytics request could not be completed."))
                if detail.get("sql"):
                    st.subheader("Rejected SQL")
                    st.code(detail["sql"], language="sql")
                if detail.get("validation"):
                    with st.expander("Validation details"):
                        st.json(detail["validation"])
                if detail.get("metrics"):
                    with st.expander("Observability"):
                        st.json(detail["metrics"])
            except ValueError:
                st.error(r.text)
    except Exception as exc:
        st.error(f"Could not reach API: {exc}")
