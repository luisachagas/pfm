# Como colocar o sistema na nuvem (para qualquer pessoa usar pelo link)

O objetivo é que **ninguém precise instalar Python, rodar código ou baixar bibliotecas**. A pessoa só abre um link no navegador e usa o sistema.

A forma mais simples e **gratuita** é usar o **Streamlit Community Cloud**.

---

## Passo a passo (resumido)

1. **Ter o projeto no GitHub**  
   - Se ainda não tiver: crie uma conta em [github.com](https://github.com), crie um repositório e suba a pasta do projeto (incluindo `app.py`, `requirements.txt`, pastas `1. UI`, `2. Data`, `.streamlit`).

2. **Deploy no Streamlit Cloud**  
   - Acesse [share.streamlit.io](https://share.streamlit.io).  
   - Faça login com a conta do GitHub.  
   - Clique em **“New app”**.  
   - Escolha: repositório = onde está o projeto, branch = `main`, arquivo = `app.py`.  
   - Clique em **“Deploy!”**.  
   - Aguarde alguns minutos. Quando terminar, o site vai mostrar um **link** (ex: `https://seu-app.streamlit.app`).

3. **Configurar credenciais AWS (obrigatório)**  
   - No Streamlit Cloud, abra o seu app e clique nos **três risquinhos** (canto inferior direito) → **“Settings”** → **“Secrets”**.  
   - Cole o conteúdo no formato abaixo (troque pelos seus valores reais):

   ```toml
   aws_access_key_id = "SUA_CHAVE_AWS"
   aws_secret_access_key = "SEU_SECRET_AWS"
   ```

   - Salve. O app vai reiniciar e passar a usar essas credenciais na nuvem.

4. **Compartilhar o link**  
   - Envie o link do app (ex: `https://seu-app.streamlit.app`) para quem for usar.  
   - Essas pessoas **só precisam abrir o link no navegador** (Chrome, Edge, etc.). Não precisam instalar nada.

---

## O que precisa estar no repositório do GitHub

- `app.py`
- `requirements.txt`
- Pasta `1. UI/` (com `cabecalho.png`, etc.)
- Pasta `2. Data/` (com `user.csv`)
- Pasta `.streamlit/` (com `config.toml`)

**Não** inclua no GitHub:

- Arquivo `.env` (credenciais ficam só em **Secrets** no Streamlit Cloud)
- Pasta `4. Petições/` (arquivos gerados na nuvem são temporários; o usuário baixa o Excel pelo botão)

---

## Diferença: uso local x na nuvem

| Onde | Como abre | Onde ficam os arquivos gerados |
|------|-----------|---------------------------------|
| **No seu PC** | `INSTALAR_EXECUTAR.bat` ou `streamlit run app.py` | Pasta `4. Petições/` no projeto |
| **Na nuvem** | Só abrir o link no navegador | Temporário; o usuário baixa o **Excel** pelo botão “Baixar dados consolidados (Excel)” |

Na nuvem, as petições em PDF e TXT são geradas em área temporária; o foco para o usuário é **baixar o Excel consolidado**. O app já está preparado para isso.

---

## Resumo para quem vai usar (pessoas leigas)

- Você recebe um **link** (ex: `https://xxxx.streamlit.app`).
- Abra esse link no **Chrome**, **Edge** ou outro navegador.
- Não é preciso instalar programa nem abrir código.
- Use o **Hub** para escolher “Extrato” e depois os módulos **Novas CDAs** ou **CDAs Ajuizadas**.
- No final, use o botão **“Baixar dados consolidados (Excel)”** para salvar o arquivo no seu computador.

Se algo der erro (por exemplo “Credenciais AWS não configuradas”), quem configurou o app na nuvem precisa ajustar os **Secrets** no Streamlit Cloud com a chave e o secret da AWS.
