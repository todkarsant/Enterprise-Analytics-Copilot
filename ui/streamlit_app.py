import os
import requests
import streamlit as st

st.set_page_config(page_title="Enterprise Analytics Copilot",layout="wide")
st.title("Enterprise Analytics Copilot")
st.caption("NL2SQL → validation → execution → business answer")

api_url=st.sidebar.text_input("API URL",os.getenv("API_URL","http://localhost:8000/api"))
question=st.text_area("Ask an analytics question", "Which stores have the highest sales?", height=100)
if st.button("Run analysis",type="primary"):
    try:
        r=requests.post(f"{api_url}/query",json={"question":question},timeout=60)
        if r.ok:
            data=r.json()
            st.subheader("Business answer")
            st.write(data["answer"])
            st.subheader("Generated SQL")
            st.code(data["sql"],language="sql")
            st.subheader("Result")
            if data["rows"]:
                st.dataframe([dict(zip(data["columns"],row)) for row in data["rows"]],use_container_width=True)
            st.subheader("Observability")
            st.json(data["metrics"])
            with st.expander("Agent trace"):
                st.json(data["trace"])
            with st.expander("Retrieved schema context"):
                st.json(data.get("schema_items",[]))
        else:
            st.error(r.text)
    except Exception as exc:
        st.error(f"Could not reach API: {exc}")
