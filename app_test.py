import streamlit as st

st.set_page_config(
    page_title="Test",
    page_icon="⚖️",
    layout="wide"
)

st.title("Test App - Se você vê isso, o Streamlit funciona!")
st.success("✅ App inicializado com sucesso")

if st.button("Testar boto3"):
    try:
        import boto3
        st.success("✅ boto3 importado")
    except Exception as e:
        st.error(f"❌ Erro no boto3: {e}")

if st.button("Testar awswrangler"):
    try:
        import awswrangler as wr
        st.success("✅ awswrangler importado")
    except Exception as e:
        st.error(f"❌ Erro no awswrangler: {e}")

if st.button("Testar user.csv"):
    try:
        import pandas as pd
        df = pd.read_csv('2. Data/user.csv', sep=';', decimal=',')
        st.success(f"✅ user.csv carregado: {len(df)} linhas")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Erro ao carregar user.csv: {e}")
