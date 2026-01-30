import streamlit as st

def main():
    st.set_page_config(
        page_title="Test Minimal",
        page_icon="⚖️",
        layout="wide"
    )
    
    st.title("✅ App funcionando!")
    st.success("Se você vê isso, o Streamlit Cloud está OK")
    
    st.write("Agora vamos testar os imports...")
    
    if st.button("Testar imports pesados"):
        with st.spinner("Importando awswrangler..."):
            try:
                import awswrangler as wr
                st.success("✅ awswrangler OK")
            except Exception as e:
                st.error(f"❌ awswrangler falhou: {e}")

if __name__ == "__main__":
    main()
