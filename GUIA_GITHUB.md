# Como subir a pasta do projeto no GitHub

Você já tem conta no GitHub. Siga um dos casos abaixo.

> **No Windows (PowerShell):** digite **apenas** os comandos abaixo, **um por vez**. Não copie as linhas `` ```bash `` ou `` ``` `` — elas são só formatação do texto.

---

## Caso 1: Este projeto já está ligado a um repositório no GitHub

Se esta pasta já foi clonada do GitHub ou já teve `git remote add` feito antes:

1. **Abra o terminal** na pasta do projeto  
   (no Cursor: Terminal → New Terminal, ou no Windows: abra o Prompt de Comando e use `cd` até a pasta).

2. **Adicione todas as alterações** (copie só esta linha):
   ```
   git add .
   ```

3. **Crie um commit** (copie só esta linha):
   ```
   git commit -m "Atualização: hub de robôs, layout extrato e deploy na nuvem"
   ```

4. **Envie para o GitHub** (copie só esta linha):
   ```
   git push origin main
   ```

Se pedir usuário e senha: use seu **usuário do GitHub** e, em vez da senha, um **Personal Access Token** (GitHub → Settings → Developer settings → Personal access tokens → Generate new token).

---

## Caso 2: Ainda não existe repositório no GitHub para este projeto

### Passo A: Criar o repositório no site do GitHub

1. Acesse [github.com](https://github.com) e faça login.
2. Clique no **+** (canto superior direito) → **New repository**.
3. Preencha:
   - **Repository name:** por exemplo `sistema-peticoes-pcr` (ou outro nome).
   - **Description:** opcional (ex: "Sistema de Petições Automáticas - PCR").
   - Deixe **Public**.
   - **Não** marque "Add a README file" (a pasta já tem arquivos).
4. Clique em **Create repository**.

### Passo B: Subir a pasta do seu PC para esse repositório

**Digite um comando por vez; não copie as linhas em branco nem `` ``` ``.**

1. **Abra o terminal na pasta do projeto** (a pasta onde está o `app.py`).

2. Se ainda **não** tiver Git nesta pasta, rode (um por vez):
   ```
   git init
   ```
   ```
   git branch -M main
   ```

3. Conecte ao repositório (troque SEU_USUARIO e NOME_DO_REPOSITORIO pelos seus):
   ```
   git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
   ```
   Exemplo: usuário `joao`, repositório `sistema-peticoes-pcr`:
   ```
   git remote add origin https://github.com/joao/sistema-peticoes-pcr.git
   ```

4. Adicione os arquivos, faça o commit e envie (um comando por vez):
   ```
   git add .
   ```
   ```
   git commit -m "Primeiro envio: Sistema PCR - Hub de Robôs e Extrato"
   ```
   ```
   git push -u origin main
   ```

5. Se pedir **login**, use:
   - **Usuário:** seu usuário do GitHub  
   - **Senha:** um **Personal Access Token** (não use a senha da conta).  
   Para criar o token: GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**. Marque permissão **repo** e use o token no lugar da senha.

---

## Resumo rápido (projeto já com Git e remote)

Rode **um comando por vez** no PowerShell (não copie `` ``` `` nem ``bash``):

```
cd "c:\Users\Lenovo\Downloads\extrato 1 (3)\extrato"
```
```
git add .
```
```
git commit -m "Atualização: hub, layout extrato, deploy nuvem"
```
```
git push origin main
```

Depois disso, o código estará no GitHub e você poderá usar o **Streamlit Cloud** (conforme o `DEPLOY_NUVEM.md`) para gerar o link que todos abrem no navegador.
