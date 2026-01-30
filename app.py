import streamlit as st
import pandas as pd
import os
import boto3
import tempfile
from dotenv import load_dotenv
import awswrangler as wr
import locale
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

# Configurações iniciais - MOVIDO PARA DENTRO DA main()

# Carrega as variáveis de ambiente (local; na nuvem usa Secrets)
load_dotenv()

# Diretório de saída: local usa "4. Petições"; na nuvem usa /tmp (disco é somente leitura)
def _get_output_dir():
    default = "4. Petições"
    try:
        os.makedirs(default, exist_ok=True)
        if os.access(default, os.W_OK):
            return default
    except Exception:
        pass
    tmp = os.path.join(tempfile.gettempdir(), "peticoes_pcr")
    os.makedirs(tmp, exist_ok=True)
    return tmp

OUTPUT_DIR = _get_output_dir()
RUNNING_IN_CLOUD = OUTPUT_DIR != "4. Petições"

# Configura o locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass

# Cores Procuradoria: azul escuro + branco
AZUL_ESCURO = "#0d47a1"
AZUL_MEIO = "#1565c0"
AZUL_CLARO = "#e3f2fd"
BRANCO = "#ffffff"
CINZA_PAGE = "#f5f7fa"

# Estilos CSS - MOVIDO PARA DENTRO DA main()
CSS_STYLES = """
    <style>
    :root {
        --azul: #0d47a1;
        --azul-meio: #1565c0;
        --azul-claro: #e3f2fd;
        --branco: #ffffff;
        --cinza: #64748b;
        --dark: #1e3a5f;
    }
    
    .stApp { background: #f5f7fa; }
    
    /* ========== HUB DE ROBÔS ========== */
    .hub-container { max-width: 900px; margin: 0 auto; padding: 2rem 1rem; }
    .hub-header {
        text-align: center;
        margin-bottom: 3rem;
    }
    .hub-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #0d47a1;
        margin-bottom: 0.5rem;
    }
    .hub-header p { color: #64748b; font-size: 1.1rem; }
    
    .hub-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(13, 71, 161, 0.1);
        border: 1px solid rgba(13, 71, 161, 0.15);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .hub-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(13, 71, 161, 0.2);
    }
    .hub-card.disabled { opacity: 0.6; pointer-events: none; }
    .hub-card .tag {
        display: inline-block;
        background: #e3f2fd;
        color: #0d47a1;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .hub-card h2 { color: #1e3a5f; font-size: 1.35rem; margin-bottom: 0.5rem; }
    .hub-card p { color: #64748b; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.25rem; }
    
    /* ========== TOP BAR (Dashboard) ========== */
    .top-bar {
        background: #0d47a1;
        padding: 0.75rem 1.5rem;
        border-radius: 0 0 12px 12px;
        margin: -1rem -1rem 1.5rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .top-bar .logo-area { display: flex; align-items: center; gap: 0.75rem; color: white; font-weight: 700; font-size: 1.1rem; }
    .top-bar .user-area { color: rgba(255,255,255,0.95); font-size: 0.95rem; }
    
    /* ========== BANNER BOAS-VINDAS ========== */
    .dashboard-banner {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 20px rgba(13, 71, 161, 0.25);
    }
    .dashboard-banner h2 { color: white; font-size: 1.75rem; margin-bottom: 0.35rem; }
    .dashboard-banner p { color: rgba(255,255,255,0.9); font-size: 1rem; margin-bottom: 1.25rem; }
    
    /* ========== CARDS MÓDULOS (estilo Running Courses) ========== */
    .running-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .running-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(13, 71, 161, 0.12);
    }
    .running-card .tag {
        display: inline-block;
        background: #e3f2fd;
        color: #0d47a1;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .running-card h3 { color: #1e3a5f; font-size: 1.15rem; margin-bottom: 0.5rem; }
    .running-card .desc { color: #64748b; font-size: 0.9rem; line-height: 1.5; margin-bottom: 1rem; }
    
    /* ========== SIDEBAR MENU (dashboard) ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0d47a1 100%);
    }
    [data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] .stRadio label div { color: #f1f5f9 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] .stCaption { color: #94a3b8 !important; }
    
    /* ========== TAGS (Você pode precisar) ========== */
    .tag-pill {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        color: #e2e8f0;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.25rem;
    }
    
    /* ========== OUTROS ========== */
    .main-header { font-size: 1.5rem; color: #0d47a1; font-weight: 700; margin-bottom: 1rem; }
    .success-box {
        background: #e8f5e9; border: 1px solid #4caf50; border-radius: 12px;
        padding: 1.25rem 1.5rem; margin: 1rem 0;
    }
    .success-box h3 { color: #2e7d32; }
    .success-box p { color: #1b5e20; }
    .info-box {
        background: #e3f2fd; border: 1px solid #0d47a1; border-radius: 12px;
        padding: 1.25rem 1.5rem; margin: 1rem 0;
    }
    .info-box h3 { color: #0d47a1; }
    .info-box ol, .info-box p { color: #1e3a5f; line-height: 1.7; }
    .step-badge {
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; background: #0d47a1; color: white;
        border-radius: 50%; font-weight: 700; font-size: 0.95rem; margin-right: 0.5rem;
    }
    .info-box code, .success-box code { background: rgba(0,0,0,0.06); padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.9em; }
    </style>
"""

def _get_aws_credentials():
    """Credenciais AWS: na nuvem usa st.secrets, local usa .env (os.getenv)"""
    key = secret = None
    try:
        if hasattr(st, "secrets") and st.secrets:
            key = st.secrets.get("aws_access_key_id")
            secret = st.secrets.get("aws_secret_access_key")
    except Exception:
        pass
    if not key:
        key = os.getenv("aws_access_key_id")
    if not secret:
        secret = os.getenv("aws_secret_access_key")
    return key, secret

# Funções auxiliares
@st.cache_resource
def init_aws_connection():
    """Inicializa conexão com AWS S3"""
    try:
        key, secret = _get_aws_credentials()
        if not key or not secret:
            st.error("Credenciais AWS não configuradas. Na nuvem: configure em Secrets. Local: use arquivo .env")
            return False
        boto3.setup_default_session(aws_access_key_id=key, aws_secret_access_key=secret)
        return True
    except Exception as e:
        st.error(f"Erro ao conectar com AWS: {e}")
        return False

@st.cache_data(ttl=3600)
def load_data_from_s3():
    """Carrega dados do S3"""
    try:
        path = 's3://aquila-ia/pcr-ciclo-tributario/extrato_cda/'
        da_merge = wr.s3.read_parquet(os.path.join(path, 'estoque.parquet'))
        return da_merge
    except Exception as e:
        st.error(f"Erro ao carregar dados do S3: {e}")
        return None

def load_user_data():
    """Carrega dados dos usuários"""
    try:
        df_user = pd.read_csv('2. Data/user.csv', sep=';', decimal=',')
        return df_user
    except Exception as e:
        # Não usar st.error aqui pois pode ser chamado antes do Streamlit inicializar
        print(f"Erro ao carregar dados de usuários: {e}")
        return None

def get_texto_peticao_base():
    """Retorna o texto base da petição"""
    return """	É oportuno esclarecer, desde já, que o Poder Judiciário constitui a última instância em que o Município do Recife busca garantir o recebimento dos tributos devidos.

	Embora haja uma parcela considerável de contribuintes, tanto pessoas físicas quanto jurídicas, que cumprem pontualmente com suas obrigações tributárias, há também aqueles que desconsideram esse dever legal.

	Assim que o inadimplemento é identificado, o Município do Recife adota as medidas administrativas  iniciais de cobrança, que podem incluir o envio de e-mails ou cartas ou mensagens no domicílio tributário eletrônico (DT-e), conforme o perfil do contribuinte. Nos casos de pessoas físicas, notificações também podem ser enviadas por meio da plataforma Gov.Br ou por SMS.

	Cabe ressaltar que, no caso das pessoas jurídicas, a inadimplência implica, automaticamente, a impossibilidade de obtenção da certidão negativa de débitos, o que causa danos significativos à operação empresarial. Embora a medida de impedir a emissão da certidão de regularidade fiscal seja severa, ela é plenamente legal e visa a promover a rápida regularização da pendência tributária.

	Dessa forma, entre o vencimento do tributo e o ajuizamento da execução fiscal, diversas ações são tomadas com o objetivo de incentivar a regularização ADMINISTRATIVA do débito por parte do contribuinte.

	Observe-se o relatório anexo, referente ao exercício 2024, que detalha a grade de envio de comunicações fiscais por parte do Município do Recife. Cada tipo de contribuinte e cada tipo de débito tem um tratamento diferente. As fôrmas utilizadas vão desde as tradicionais cartas físicas, passando pelos e-mails, chegando nas mensagens do DT-e. Em 2024, foram enviados mais de 7 milhões de disparos! As mensagens normalmente são enviadas preventivamente (avisando que existe um débito a vencer), como corretivamente (após o vencimento do débito). As mensagens corretivas são enviadas desde os primeiros dias de inadimplemento até a inscrição em dívida ativa. Também são enviadas mensagens pela Procuradoria, após a inscrição em dívida ativa, mas antes do protesto, como um estímulo ao pagamento sem custas e emolumentos.

	A título de exemplo, o Exequente acosta uma planilha que trata do caso de um contribuinte específico. Foram dezenas de mensagens enviadas previamente ao ajuizamento da execução fiscal.

	Nessas mensagens, em qualquer que seja a fase, normalmente é destacada a importância de o débito ser quitado o quanto antes, em virtude da incidência de juros e multa, assim como, no geral, são informadas as condições de pagamento (à vista/parcelado). Algumas mensagens se fazem acompanhar de DAM para pagamento. Em todas elas, é disponibilizado o contato da Secretaria de Finanças ou da Procuradoria, conforme o caso.

	Em resumo, o ajuizamento da execução fiscal configura-se, portanto, como uma medida extrema, visto que, para o Município do Recife, é de seu interesse que o crédito tributário seja quitado o quanto antes.

	Para os Exequentes, seria preferível não recorrer ao Poder Judiciário para a cobrança de seus créditos, mas existem determinadas providências que só podem ser implementadas por este, como a constrição de bens.

	Com essas considerações iniciais, que refletem fielmente os procedimentos adotados pelo Município do Recife, passa-se, então, a analisar o despacho proferido, que faz menção à Resolução nº 547/2024 – CNJ.

	Segundo a Resolução n. 547/2024 – CNJ, "a tentativa de conciliação pode ser satisfeita, exemplificativamente, pela existência de lei geral de parcelamento ou oferecimento de algum tipo de vantagem na via administrativa, como redução ou extinção de juros ou multas, ou oportunidade concreta de transação na qual o executado, em tese, se enquadre" (§1º do art. 2º).

	No caso do Município do Recife, o Código Tributário Municipal, art. 164 prevê:

Art. 164. Os débitos tributários em fase judicial, de um mesmo contribuinte, até a etapa anterior à destinação do bem à hasta pública, poderão ser parcelados em até 60 (sessenta) parcelas mensais e sucessivas, observado o valor mínimo de cada parcela de R$ 50,00 (cinquenta reais). 

	Portanto, observa-se que o débito pode ser parcelado em até 60 vezes.

	Mas não existe apenas essa opção de pagamento. O contribuinte pode parcelar em 12 vezes, 24 vezes ou até pagar à vista e alcançar uma expressiva redução de juros e de multa, a depender da opção. Veja-se: 

Art. 172. Os débitos municipais poderão ser quitados em parcela única e ou parcelados mediante acordo, observadas as seguintes disposições:

I – O débito poderá ser parcelado da seguinte forma e nas seguintes condições:

a) dividido em até 12 (doze) parcelas mensais e sucessivas, com redução de 40% (quarenta por cento) da multa de mora, da multa de infração, dos juros de mora e da atualização monetária;

b) dividido de 13 (treze) até 24 (vinte e quatro) parcelas mensais e sucessivas, com redução de 20% (vinte por cento) da multa de mora, da multa de infração, dos juros de mora e da atualização monetária;

c) dividido de 25 (vinte e cinco) até 36 (trinta e seis) parcelas mensais e sucessivas, com redução de 15% (quinze por cento) dos juros de mora e da atualização monetária;

d) dividido de 37 (trinta e sete) até 60 (sessenta) parcelas mensais e sucessivas, sem qualquer redução;

	Sendo assim, possível a redução de até 40% de juros, de multa de mora, de multa de infração e de atualização monetária.

	Por outro lado, caso o contribuinte opte por pagar à vista, as reduções são ainda maiores, sendo possível o alcance de uma redução de até 80% da multa de infração. Veja-se: 

II - Sendo o débito quitado em parcela única, aplicar-se-á, conforme o caso, as seguintes reduções:

a) para os débitos ajuizados: redução de 50% (cinquenta por cento) da multa de mora, dos juros de mora e da atualização monetária, acrescida da redução de 80% (oitenta por cento) do valor da multa de infração.

b) para os débitos inscritos em Dívida Ativa e ainda não ajuizados: redução de 60% (sessenta por cento) da multa de mora, dos juros de mora e da atualização monetária, acrescida da redução de 80% (oitenta por cento) do valor da multa de infração;

c) para os demais débitos: redução de 70% (setenta por cento) da multa de mora, dos juros de mora e da atualização monetária, acrescida da redução de 80% (oitenta por cento) do valor da multa de infração;

	Portanto, existem evidentes benefícios concedidos pela Fazenda Municipal na via administrativa. Tudo isso facilita e é mais célere ao contribuinte do que negociar em juízo.

	Mesmo em juízo, a Fazenda aceita o parcelamento de 60 (sessenta) vezes e, se necessário, aceita o parcelamento em prazo superior, mediante apresentação de plano de pagamento.

	Todas essas alternativas de pagamento estão disponíveis ao executado na página da Prefeitura do Recife na internet, que orienta detalhadamente sobre os passos a serem observados para a regularização do débito tributário: "https://recife.pe.gov.br/servicos-on-line/parcelamento-de-debitos-em-qualquer-fase"

	Destaca-se ainda que, embora na fase de ajuizamento não seja mais possível redução, o parcelamento pode ser feito mesmo depois de levada a dívida ativa ao judiciário. A referida forma de pagamento é alternativa essencial para incentivar o inadimplente a quitar seus débitos.

	No tocante às especificações do caso concreto, a CDA passará por análise no que pertine à obrigação de cobrança extrajudicial.
"""

def criar_peticao_texto(numero_cda, nome_executado="*INSERIR*", numero_execucao=None, mat_oab=None, mat_pfm=None):
    """Cria o texto completo da petição"""
    if numero_execucao:
        cabecalho = f"""EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA VARA DOS EXECUTIVOS FISCAIS MUNICIPAIS DA CAPITAL DA COMARCA DE RECIFE




Execução Fiscal Nº {numero_execucao}
Exequente: MUNICIPIO DO RECIFE
Exequente/Executado: {nome_executado}

	

	MUNICÍPIO DO RECIFE, já qualificado nos autos, vem, perante V. Exa., através do procurador abaixo assinado, em atenção ao despacho proferido, expor o que segue para ao final requerer.

	Cuida-se de despacho que questiona se o Município do Recife adotou medidas administrativas de cobrança antes do ajuizamento da execução fiscal.
"""
    else:
        cabecalho = f"""EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA VARA DOS EXECUTIVOS FISCAIS MUNICIPAIS DA CAPITAL DA COMARCA DE RECIFE



CDA: {numero_cda}
Exequente: MUNICIPIO DO RECIFE
Exequente/Executado: {nome_executado}

	

	MUNICÍPIO DO RECIFE, já qualificado nos autos, vem, perante V. Exa., através do procurador abaixo assinado, em atenção ao despacho proferido, expor o que segue para ao final requerer.

	Cuida-se de despacho que questiona se o Município do Recife adotou medidas administrativas de cobrança antes do ajuizamento da execução fiscal.
"""
    
    rodape = f"""
	Diante do exposto, requer-se:

a) que seja juntada aos autos a presente peça e os documentos em anexo como prova das medidas administrativas adotadas;

b) que, uma vez demonstrada a conformidade com a Resolução 547/2024 do CNJ, prossiga-se no feito.

	Termos em que,
	Pede deferimento.


	Recife, {datetime.now().strftime('%d de %B de %Y')}.


PROCURADOR DO MUNICÍPIO
"""
    
    if mat_oab and mat_pfm:
        rodape += f"MAT. OAB/PE {mat_oab}\nMAT. PFM {mat_pfm}"
    
    return cabecalho + get_texto_peticao_base() + rodape

def criar_extrato_pdf(row, da_merge_row, output_filename):
    """Cria PDF do extrato de ações administrativas"""
    try:
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=0,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        elements = []

        # Verificar se existe cabeçalho
        if os.path.exists('1. UI/cabecalho.png'):
            cabecalho_img = Image('1. UI/cabecalho.png', 
                                width=doc.width + doc.leftMargin + doc.rightMargin, 
                                height=1.5*inch)
            elements.append(cabecalho_img)
        
        elements.append(Spacer(1, 24))

        # Título
        titulo_style = ParagraphStyle(
            name='Titulo',
            parent=styles['Heading1'],
            fontSize=14,
            leading=18,
            alignment=1,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        titulo = Paragraph('EXTRATO DE AÇÕES ADMINISTRATIVAS DA CERTIDÃO DE DÍVIDA ATIVA', titulo_style)
        elements.append(titulo)
        elements.append(Spacer(1, 24))

        # Texto principal
        justified_style = ParagraphStyle(
            name='Justified',
            parent=styles['BodyText'],
            fontSize=12,
            leading=18,
            alignment=4,
            spaceAfter=12
        )

        tipo_divida = str(da_merge_row['tipo_divida']).lower()
        inscricao_divida = da_merge_row['inscricao_divida']
        id_contribuinte = da_merge_row['id_contribuinte_formatado']
        id_entidade = str(da_merge_row['id_entidade']).replace('.0', '')
        
        if tipo_divida == 'imovel':
            texto = f"Em conformidade com a Resolução 547/2024 do CNJ, a Procuradoria da Fazenda Municipal do Recife certifica que a CDA {row['cda']}, inscrita na data {inscricao_divida}, referente ao contribuinte de documento {id_contribuinte} e ao sequencial imobiliário cadastrado sob o número {id_entidade}, foi submetida às seguintes medidas, conforme detalhado na tabela abaixo:"
        else:
            texto = f"Em conformidade com a Resolução 547/2024 do CNJ, a Procuradoria da Fazenda Municipal do Recife certifica que a CDA {row['cda']}, inscrita na data {inscricao_divida}, referente ao contribuinte de documento {id_contribuinte} e a inscrição mercantil cadastrada sob o número {id_entidade}, foi submetida às seguintes medidas, conforme detalhado na tabela abaixo:"

        elements.append(Paragraph(texto, justified_style))
        elements.append(Spacer(1, 24))

        # Função para formatar valores
        def format_value(value):
            if pd.isna(value) or value in [None, '']:
                return '-'
            return str(value)

        # Construir dados da tabela
        sms = da_merge_row['sms'] if pd.notna(da_merge_row['sms']) else 0
        email = da_merge_row['email'] if pd.notna(da_merge_row['email']) else 0
        contato_admin = 'SIM' if (sms + email) > 0 else 'NÃO'

        neg_quod = da_merge_row['negativacao_quod'] if pd.notna(da_merge_row['negativacao_quod']) else 0
        neg_scpc = da_merge_row['negativacao_scpc'] if pd.notna(da_merge_row['negativacao_scpc']) else 0
        negativada = 'SIM' if (neg_quod + neg_scpc) > 0 else 'NÃO'

        protesto = da_merge_row['protesto'] if pd.notna(da_merge_row['protesto']) else 0
        protestada = 'SIM' if protesto == 1 else 'NÃO'

        ajuizamento = da_merge_row['ajuizamento'] if pd.notna(da_merge_row['ajuizamento']) else 0
        ajuizada = 'SIM' if ajuizamento == 1 else 'NÃO'

        data = [
            ['CERTIDÃO DE DÍVIDA ATIVA:', row['cda']],
            ['DOCUMENTO DO CONTRIBUINTE:', id_contribuinte],
            ['SEQUENCIAL DO IMÓVEL/INSCRIÇÃO MERCANTIL:', id_entidade],
            ['TIPO DA DÍVIDA:', tipo_divida.upper()],
            ['CONTRIBUINTE CONTACTADO ADMINISTRATIVAMENTE?', contato_admin],
            ['CDA NEGATIVADA?', negativada],
            ['CDA PROTESTADA?', protestada],
            ['CDA AJUIZADA?', ajuizada],
            ['DATA DE COMUNICAÇÃO (SMS):', format_value(da_merge_row['data_sms'])],
            ['DATA DE COMUNICAÇÃO (E-MAIL):', format_value(da_merge_row['data_email'])],
            ['DATA DE NEGATIVAÇÃO (QUOD):', format_value(da_merge_row['data_negativacao_quod'])],
            ['DATA DE NEGATIVAÇÃO (SCPC):', format_value(da_merge_row['data_negativacao_scpc'])]
        ]

        # Estilo da tabela
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B2E3D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F2F2F2')),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ])

        table = Table(data, colWidths=[300, 140])
        table.setStyle(table_style)
        elements.append(table)

        # Rodapé
        data_sistema = datetime.now().strftime('%d/%m/%Y')
        footer_text = f"<i>Relatório gerado em {data_sistema}. Fonte de dados: Emprel</i>"
        footer_style = ParagraphStyle(
            name='FooterStyle',
            parent=styles['Italic'],
            fontSize=10,
            alignment=1
        )
        elements.append(Spacer(1, 24))
        elements.append(Paragraph(footer_text, footer_style))

        # Gerar PDF
        doc.build(elements)
        return True
    except Exception as e:
        st.error(f"Erro ao criar PDF: {e}")
        return False

def processar_modulo_novas_cdas(df_input, da_merge, usuario_selecionado, df_user):
    """Processa módulo de novas CDAs"""
    try:
        # Criar diretório de saída (OUTPUT_DIR já definido no início do app)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Buscar dados do usuário
        usuario_info = df_user[df_user['user'] == usuario_selecionado]
        mat_oab = usuario_info['mat_oab'].values[0] if not usuario_info.empty else None
        mat_pfm = usuario_info['mat_pfm'].values[0] if not usuario_info.empty else None
        
        peticoes_geradas = []
        erros = []
        
        # Preparar dados
        da_merge['cda'] = da_merge['cda'].astype(str).str.strip()
        df_input['cda'] = df_input['cda'].astype(str).str.strip()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total = len(df_input)
        
        for idx, row in df_input.iterrows():
            try:
                numero = row['cda']
                status_text.text(f"Processando CDA {numero}... ({idx+1}/{total})")
                
                # Buscar CDA
                resultado = da_merge[da_merge['cda'] == numero]
                
                if resultado.empty:
                    erros.append(f"CDA {numero} não encontrada")
                    continue
                
                da_merge_row = resultado.iloc[0]
                
                # Gerar petição
                texto_peticao = criar_peticao_texto(
                    numero_cda=numero,
                    mat_oab=mat_oab,
                    mat_pfm=mat_pfm
                )
                
                # Salvar petição
                with open(os.path.join(OUTPUT_DIR, f'{numero}_peticao.txt'), 'w', encoding='utf-8') as f:
                    f.write(texto_peticao)
                
                # Criar extrato PDF
                criar_extrato_pdf(row, da_merge_row, os.path.join(OUTPUT_DIR, f'{numero}_extrato.pdf'))
                
                peticoes_geradas.append(numero)
                progress_bar.progress((idx + 1) / total)
                
            except Exception as e:
                erros.append(f"Erro ao processar CDA {row['cda']}: {str(e)}")
        
        status_text.empty()
        progress_bar.empty()
        
        # Merge final
        df_merged = pd.merge(
            df_input,
            da_merge[['cda', 'id_entidade', 'id_contribuinte_formatado', 'tipo_divida', 
                     'tipo_tributo', 'inscricao_divida', 'ajuizamento_divida', 'da_aberto',
                     'ajuizamento', 'protesto', 'negativacao_quod', 'data_negativacao_quod',
                     'negativacao_scpc', 'data_negativacao_scpc', 'sms', 'data_sms', 
                     'email', 'data_email']],
            how='left',
            on='cda'
        )
        
        df_merged['tipo_divida'] = df_merged['tipo_divida'].astype(str)
        df_merged['id_entidade'] = df_merged['id_entidade'].astype(str).str.replace('.0', '')
        df_merged.dropna(subset=['cda', 'tipo_divida'], inplace=True)
        
        # Salvar Excel
        df_merged.to_excel(os.path.join(OUTPUT_DIR, 'dados_retorno.xlsx'), index=False)
        
        return peticoes_geradas, erros, df_merged
        
    except Exception as e:
        st.error(f"Erro no processamento: {e}")
        return [], [str(e)], None

def processar_modulo_cdas_ajuizadas(df_input, da_merge, usuario_selecionado, df_user):
    """Processa módulo de CDAs já ajuizadas"""
    try:
        # Criar diretório de saída
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Buscar dados do usuário
        usuario_info = df_user[df_user['user'] == usuario_selecionado]
        mat_oab = usuario_info['mat_oab'].values[0] if not usuario_info.empty else None
        mat_pfm = usuario_info['mat_pfm'].values[0] if not usuario_info.empty else None
        
        peticoes_geradas = []
        erros = []
        
        # Preparar dados
        da_merge['cda'] = da_merge['cda'].astype(str).str.strip()
        df_input['cda'] = df_input['cda'].astype(str).str.strip()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total = len(df_input)
        
        for idx, row in df_input.iterrows():
            try:
                numero = row['cda']
                nome = row['nome_executado']
                exec_num = row['numero_execucao']
                
                status_text.text(f"Processando execução {exec_num}... ({idx+1}/{total})")
                
                # Buscar CDA
                resultado = da_merge[da_merge['cda'] == numero]
                
                if resultado.empty:
                    erros.append(f"CDA {numero} não encontrada")
                    continue
                
                da_merge_row = resultado.iloc[0]
                
                # Gerar petição
                texto_peticao = criar_peticao_texto(
                    numero_cda=numero,
                    nome_executado=nome,
                    numero_execucao=exec_num,
                    mat_oab=mat_oab,
                    mat_pfm=mat_pfm
                )
                
                # Salvar petição
                with open(os.path.join(OUTPUT_DIR, f'{exec_num}_peticao.txt'), 'w', encoding='utf-8') as f:
                    f.write(texto_peticao)
                
                # Criar extrato PDF
                criar_extrato_pdf(row, da_merge_row, os.path.join(OUTPUT_DIR, f'{exec_num}_extrato.pdf'))
                
                peticoes_geradas.append(exec_num)
                progress_bar.progress((idx + 1) / total)
                
            except Exception as e:
                erros.append(f"Erro ao processar execução {row['numero_execucao']}: {str(e)}")
        
        status_text.empty()
        progress_bar.empty()
        
        # Merge final
        df_merged = pd.merge(
            df_input,
            da_merge[['cda', 'id_entidade', 'id_contribuinte_formatado', 'tipo_divida',
                     'tipo_tributo', 'inscricao_divida', 'ajuizamento_divida', 'da_aberto',
                     'ajuizamento', 'protesto', 'negativacao_quod', 'data_negativacao_quod',
                     'negativacao_scpc', 'data_negativacao_scpc', 'sms', 'data_sms',
                     'email', 'data_email']],
            how='left',
            on='cda'
        )
        
        df_merged['tipo_divida'] = df_merged['tipo_divida'].astype(str)
        df_merged['id_entidade'] = df_merged['id_entidade'].astype(str).str.replace('.0', '')
        
        # Salvar Excel
        df_merged.to_excel(os.path.join(OUTPUT_DIR, 'dados_retorno.xlsx'), index=False)
        
        return peticoes_geradas, erros, df_merged
        
    except Exception as e:
        st.error(f"Erro no processamento: {e}")
        return [], [str(e)], None

# Caminho do Excel de retorno (para download)
def _excel_retorno_path():
    return os.path.join(OUTPUT_DIR, 'dados_retorno.xlsx')

# Interface principal
def main():
    # DEVE SER A PRIMEIRA CHAMADA STREAMLIT
    st.set_page_config(
        page_title="Sistema PCR — Hub de Robôs",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Aplicar estilos CSS
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    # Estado: hub (seleção de robôs) ou extrato (petições)
    if 'tela_atual' not in st.session_state:
        st.session_state.tela_atual = "hub"
    if 'modulo' not in st.session_state:
        st.session_state.modulo = "🏠 Início"
    
    # ---------- HUB DE ROBÔS (tela inicial) ----------
    if st.session_state.tela_atual == "hub":
        with st.sidebar:
            cabecalho_path = os.path.join("1. UI", "cabecalho.png")
            if os.path.exists(cabecalho_path):
                st.image(cabecalho_path, use_container_width=True)
            else:
                st.markdown("""
                <div style="background: #0d47a1; padding: 1rem; border-radius: 12px; text-align: center; color: white; font-weight: 700; font-size: 1.1rem;">PCR</div>
                """, unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("### Hub de Robôs")
            st.caption("Selecione o robô abaixo para acessar.")
            st.markdown("---")
            st.caption("Sistema PCR · Versão 2.0  \n© 2024 Procuradoria do Recife")
        
        st.markdown("""
        <div class="hub-container">
            <div class="hub-header">
                <h1>Hub de Robôs — Procuradoria do Recife</h1>
                <p>Selecione o robô que deseja utilizar. Novos robôs serão disponibilizados em breve.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="hub-card">
                <span class="tag">Petições / Extrato</span>
                <h2>Petições Automáticas — Extrato CDA</h2>
                <p>Gera petições e extratos em conformidade com a Resolução CNJ 547/2024. Módulos: Novas CDAs e CDAs Ajuizadas.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Extrato", type="primary", use_container_width=True, key="hub_extrato"):
                st.session_state.tela_atual = "extrato"
                st.session_state.modulo = "🏠 Início"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="hub-card disabled">
                <span class="tag">Em breve</span>
                <h2>Novos robôs</h2>
                <p>Outros robôs serão integrados ao hub em atualizações futuras.</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("Em breve", use_container_width=True, key="hub_breve", disabled=True)
        
        return
    
    # ---------- DENTRO DO EXTRATO (layout dashboard) ----------
    # Carregar usuários para exibir no topo (se disponível)
    df_user = None
    try:
        df_user = load_user_data()
    except Exception:
        pass
    
    # Top bar (barra superior estilo dashboard)
    user_label = "Usuário"
    if df_user is not None and not df_user.empty:
        usuarios = df_user['user'].tolist()
        default_idx = 0
        if 'usuario_extrato' in st.session_state and st.session_state.usuario_extrato in usuarios:
            default_idx = usuarios.index(st.session_state.usuario_extrato)
        user_label = usuarios[default_idx] if default_idx < len(usuarios) else usuarios[0]
    
    cabecalho_path = os.path.join("1. UI", "cabecalho.png")
    st.markdown(f"""
    <div class="top-bar">
        <div class="logo-area">
            <span style="font-size: 1.25rem;">⚖️</span>
            <span>Petições Automáticas — Extrato</span>
        </div>
        <div class="user-area">Olá, <strong>{user_label}</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar do Extrato
    with st.sidebar:
        if os.path.exists(cabecalho_path):
            st.image(cabecalho_path, use_container_width=True)
        else:
            st.markdown('<div style="background: #1e3a5f; padding: 0.75rem; border-radius: 8px; color: white; font-weight: 700; text-align: center;">PCR — Extrato</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        if st.button("← Voltar ao Hub", use_container_width=True, key="voltar_hub"):
            st.session_state.tela_atual = "hub"
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Extrato — Navegação**")
        
        modulo = st.radio(
            "Menu",
            ["🏠 Início", "📝 Novas CDAs", "⚖️ CDAs Ajuizadas"],
            index=["🏠 Início", "📝 Novas CDAs", "⚖️ CDAs Ajuizadas"].index(st.session_state.modulo),
            key='menu_radio',
            label_visibility="collapsed"
        )
        st.session_state.modulo = modulo
        
        st.markdown("---")
        st.markdown("**Você pode precisar**")
        st.markdown("""
        <div style="margin-top: 0.5rem;">
            <span class="tag-pill">CNJ 547/2024</span>
            <span class="tag-pill">Parcelamento</span>
            <span class="tag-pill">Dívida ativa</span>
            <span class="tag-pill">CDA</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.caption("Sistema de Petições · © 2024 Procuradoria do Recife")
    
    # Conteúdo: Início do Extrato (banner + cards estilo Running Courses)
    if modulo == "🏠 Início":
        st.markdown("""
        <div class="dashboard-banner">
            <h2>Bem-vindo ao Extrato de Petições</h2>
            <p>Gere petições e extratos em conformidade com a Resolução CNJ 547/2024. Escolha o módulo abaixo para começar.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Módulos disponíveis**")
        st.markdown("")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="running-card">
                <span class="tag">Novas CDAs</span>
                <h3>Petições para CDAs não ajuizadas</h3>
                <p class="desc">Entrada: CSV/Excel com coluna <code>cda</code>. Saída: petições (.txt) e extratos (.pdf).</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Novas CDAs", type="primary", use_container_width=True, key="btn_novas"):
                st.session_state.modulo = "📝 Novas CDAs"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="running-card">
                <span class="tag">CDAs Ajuizadas</span>
                <h3>Petições para execuções fiscais</h3>
                <p class="desc">Entrada: <code>cda</code>, <code>nome_executado</code>, <code>numero_execucao</code>. Saída: petições e extratos.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar CDAs Ajuizadas", type="primary", use_container_width=True, key="btn_ajuizadas"):
                st.session_state.modulo = "⚖️ CDAs Ajuizadas"
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div class="info-box">
            <h3>📋 Como usar</h3>
            <ol>
                <li>Clique em um dos módulos acima</li>
                <li>Selecione o usuário responsável e envie o arquivo CSV ou Excel</li>
                <li>Aguarde o processamento e baixe os arquivos em <code>4. Petições/</code> e o Excel consolidado</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Módulo Novas CDAs
    elif modulo == "📝 Novas CDAs":
        st.markdown("### 📝 Geração de Petições para Novas CDAs")
        st.markdown("")
        
        st.markdown("""
        <div class="info-box">
        <strong>ℹ️ Sobre este módulo</strong><br>
        Processa CDAs que ainda não foram ajuizadas. O arquivo deve conter pelo menos uma coluna chamada <code>cda</code> com os números das certidões.
        </div>
        """, unsafe_allow_html=True)
        
        # Inicializar conexão
        if not init_aws_connection():
            st.error("Erro ao conectar com AWS. Verifique as credenciais no arquivo .env")
            return
        
        # Carregar dados
        with st.spinner("Carregando dados do S3..."):
            da_merge = load_data_from_s3()
        
        if da_merge is None:
            st.error("Não foi possível carregar os dados do S3")
            return
        
        df_user = load_user_data()
        if df_user is None:
            st.error("Não foi possível carregar dados de usuários")
            return
        
        st.success(f"✅ **{len(da_merge):,}** CDAs disponíveis para consulta")
        
        st.markdown("---")
        st.markdown('<span class="step-badge">1</span> **Selecione o usuário responsável**', unsafe_allow_html=True)
        st.markdown("")
        usuarios = df_user['user'].tolist()
        usuario_selecionado = st.selectbox("Usuário:", usuarios, key="user_novas", label_visibility="collapsed")
        st.session_state.usuario_extrato = usuario_selecionado
        
        st.markdown("---")
        st.markdown('<span class="step-badge">2</span> **Envie o arquivo com as CDAs**', unsafe_allow_html=True)
        st.markdown("")
        uploaded_file = st.file_uploader(
            "Arquivo CSV ou Excel com coluna 'cda'",
            type=['csv', 'xlsx', 'xls'],
            key='upload_novas'
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_input = pd.read_csv(uploaded_file)
                else:
                    df_input = pd.read_excel(uploaded_file)
                
                st.success(f"✅ **{len(df_input)}** registros carregados")
                
                with st.expander("👁️ Visualizar dados"):
                    st.dataframe(df_input.head(10))
                
                st.markdown("---")
                st.markdown('<span class="step-badge">3</span> **Processar petições**', unsafe_allow_html=True)
                st.markdown("")
                if st.button("🚀 Gerar Petições e Extratos", type="primary", key='processar_novas'):
                    peticoes, erros, df_merged = processar_modulo_novas_cdas(
                        df_input, da_merge, usuario_selecionado, df_user
                    )
                    
                    if peticoes:
                        msg_local = "Arquivos salvos em <code>4. Petições/</code>."
                        msg_cloud = "Baixe o Excel abaixo e os PDFs/TXT pelo botão de download de cada arquivo (em breve)."
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Processamento concluído!</h3>
                            <p><strong>{len(peticoes)}</strong> petições e extratos gerados. {msg_cloud if RUNNING_IN_CLOUD else msg_local}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("📋 CDAs processadas"):
                            st.write(peticoes)
                        
                        if df_merged is not None:
                            excel_path = _excel_retorno_path()
                            if os.path.exists(excel_path):
                                with open(excel_path, 'rb') as f:
                                    st.download_button(
                                        label="📥 Baixar dados consolidados (Excel)",
                                        data=f.read(),
                                        file_name='dados_retorno.xlsx',
                                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                        key='dl_excel_novas'
                                    )
                    
                    if erros:
                        st.error("⚠️ Erros encontrados:")
                        for erro in erros:
                            st.warning(erro)
            
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")
    
    # Módulo CDAs Ajuizadas
    elif modulo == "⚖️ CDAs Ajuizadas":
        st.markdown("### ⚖️ Geração de Petições para CDAs Ajuizadas")
        st.markdown("")
        
        st.markdown("""
        <div class="info-box">
        <strong>ℹ️ Sobre este módulo</strong><br>
        Processa CDAs já ajuizadas em execuções fiscais. O arquivo deve conter as colunas: <code>cda</code>, <code>nome_executado</code> e <code>numero_execucao</code>.
        </div>
        """, unsafe_allow_html=True)
        
        if not init_aws_connection():
            st.error("Erro ao conectar com AWS. Verifique as credenciais no arquivo .env")
            return
        
        with st.spinner("Carregando dados do S3..."):
            da_merge = load_data_from_s3()
        
        if da_merge is None:
            st.error("Não foi possível carregar os dados do S3")
            return
        
        df_user = load_user_data()
        if df_user is None:
            st.error("Não foi possível carregar dados de usuários")
            return
        
        st.success(f"✅ **{len(da_merge):,}** CDAs disponíveis para consulta")
        
        st.markdown("---")
        st.markdown('<span class="step-badge">1</span> **Selecione o usuário responsável**', unsafe_allow_html=True)
        st.markdown("")
        usuarios = df_user['user'].tolist()
        usuario_selecionado = st.selectbox("Usuário:", usuarios, key="user_ajuizadas", label_visibility="collapsed")
        st.session_state.usuario_extrato = usuario_selecionado
        
        st.markdown("---")
        st.markdown('<span class="step-badge">2</span> **Envie o arquivo com as execuções**', unsafe_allow_html=True)
        st.markdown("")
        uploaded_file = st.file_uploader(
            "Arquivo CSV ou Excel com colunas: 'cda', 'nome_executado', 'numero_execucao'",
            type=['csv', 'xlsx', 'xls'],
            key='upload_ajuizadas'
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_input = pd.read_csv(uploaded_file)
                else:
                    df_input = pd.read_excel(uploaded_file)
                
                # Validar colunas necessárias
                required_cols = ['cda', 'nome_executado', 'numero_execucao']
                missing_cols = [col for col in required_cols if col not in df_input.columns]
                
                if missing_cols:
                    st.error(f"⚠️ Colunas faltando no arquivo: {', '.join(missing_cols)}")
                else:
                    st.success(f"✅ **{len(df_input)}** registros carregados")
                    
                    with st.expander("👁️ Visualizar dados"):
                        st.dataframe(df_input.head(10))
                    
                    st.markdown("---")
                    st.markdown('<span class="step-badge">3</span> **Processar petições**', unsafe_allow_html=True)
                    st.markdown("")
                    if st.button("🚀 Gerar Petições e Extratos", type="primary", key='processar_ajuizadas'):
                        peticoes, erros, df_merged = processar_modulo_cdas_ajuizadas(
                            df_input, da_merge, usuario_selecionado, df_user
                        )
                        
                        if peticoes:
                            msg_local = "Arquivos salvos em <code>4. Petições/</code>."
                            msg_cloud = "Baixe o Excel abaixo."
                            st.markdown(f"""
                            <div class="success-box">
                                <h3>✅ Processamento concluído!</h3>
                                <p><strong>{len(peticoes)}</strong> petições e extratos gerados. {msg_cloud if RUNNING_IN_CLOUD else msg_local}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander("📋 Execuções processadas"):
                                st.write(peticoes)
                            
                            if df_merged is not None:
                                excel_path = _excel_retorno_path()
                                if os.path.exists(excel_path):
                                    with open(excel_path, 'rb') as f:
                                        st.download_button(
                                            label="📥 Baixar dados consolidados (Excel)",
                                            data=f.read(),
                                            file_name='dados_retorno.xlsx',
                                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                            key='dl_excel_ajuizadas'
                                        )
                        
                        if erros:
                            st.error("⚠️ Erros encontrados:")
                            for erro in erros:
                                st.warning(erro)
            
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")

if __name__ == "__main__":
    main()