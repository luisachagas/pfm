import streamlit as st
import pandas as pd
import os
import boto3
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

# Configurações iniciais
st.set_page_config(
    page_title="Sistema de Petições Automáticas",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carrega as variáveis de ambiente
load_dotenv()

# Configura o locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass

# Estilos CSS customizados
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2B2E3D;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .module-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Funções auxiliares
@st.cache_resource
def init_aws_connection():
    """Inicializa conexão com AWS S3"""
    try:
        boto3.setup_default_session(
            aws_access_key_id=os.getenv("aws_access_key_id"),
            aws_secret_access_key=os.getenv("aws_secret_access_key")
        )
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
        st.error(f"Erro ao carregar dados de usuários: {e}")
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
        # Criar diretório de saída
        os.makedirs('4. Petições', exist_ok=True)
        
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
                with open(f'4. Petições/{numero}_peticao.txt', 'w', encoding='utf-8') as f:
                    f.write(texto_peticao)
                
                # Criar extrato PDF
                criar_extrato_pdf(row, da_merge_row, f'4. Petições/{numero}_extrato.pdf')
                
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
        df_merged.to_excel('dados_retorno.xlsx', index=False)
        
        return peticoes_geradas, erros, df_merged
        
    except Exception as e:
        st.error(f"Erro no processamento: {e}")
        return [], [str(e)], None

def processar_modulo_cdas_ajuizadas(df_input, da_merge, usuario_selecionado, df_user):
    """Processa módulo de CDAs já ajuizadas"""
    try:
        # Criar diretório de saída
        os.makedirs('4. Petições', exist_ok=True)
        
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
                with open(f'4. Petições/{exec_num}_peticao.txt', 'w', encoding='utf-8') as f:
                    f.write(texto_peticao)
                
                # Criar extrato PDF
                criar_extrato_pdf(row, da_merge_row, f'4. Petições/{exec_num}_extrato.pdf')
                
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
        df_merged.to_excel('dados_retorno.xlsx', index=False)
        
        return peticoes_geradas, erros, df_merged
        
    except Exception as e:
        st.error(f"Erro no processamento: {e}")
        return [], [str(e)], None

# Interface principal
def main():
    st.markdown('<h1 class="main-header">⚖️ Sistema de Petições Automáticas - PCR</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/2B2E3D/FFFFFF?text=PCR", use_container_width=True)
        st.title("Menu de Navegação")
        
        # Inicializar modulo no session_state se não existir
        if 'modulo' not in st.session_state:
            st.session_state.modulo = "🏠 Início"
        
        modulo = st.radio(
            "Selecione o módulo:",
            ["🏠 Início", "📝 Novas CDAs", "⚖️ CDAs Ajuizadas"],
            index=["🏠 Início", "📝 Novas CDAs", "⚖️ CDAs Ajuizadas"].index(st.session_state.modulo),
            key='menu_radio'
        )
        
        # Atualizar session_state
        st.session_state.modulo = modulo
        
        st.divider()
        
        # Informações do sistema
        st.caption("**Sistema de Petições Automáticas**")
        st.caption("Versão 2.0")
        st.caption("© 2024 Procuradoria do Recife")
    
    # Tela Inicial
    if modulo == "🏠 Início":
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2>Bem-vindo ao Sistema de Petições Automáticas</h2>
            <p style="font-size: 1.2rem; color: #666;">Selecione o módulo que deseja utilizar:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Criar duas colunas para os botões
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="module-card">
                <h2 style="text-align: center;">📝 Novas CDAs</h2>
                <p style="text-align: center;">Gera petições e extratos para CDAs que ainda não foram ajuizadas.</p>
                <ul>
                    <li>Entrada: Arquivo CSV/Excel com coluna 'cda'</li>
                    <li>Saída: Petições (.txt) e Extratos (.pdf)</li>
                    <li>Identificação: Número da CDA</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Acessar Módulo Novas CDAs", use_container_width=True, type="primary", key="btn_novas"):
                st.session_state.modulo = "📝 Novas CDAs"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="module-card">
                <h2 style="text-align: center;">⚖️ CDAs Ajuizadas</h2>
                <p style="text-align: center;">Gera petições e extratos para CDAs já ajuizadas em execuções fiscais.</p>
                <ul>
                    <li>Entrada: CSV/Excel com 'cda', 'nome_executado', 'numero_execucao'</li>
                    <li>Saída: Petições (.txt) e Extratos (.pdf)</li>
                    <li>Identificação: Número da execução</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Acessar Módulo CDAs Ajuizadas", use_container_width=True, type="primary", key="btn_ajuizadas"):
                st.session_state.modulo = "⚖️ CDAs Ajuizadas"
                st.rerun()
        
        st.divider()
        
        st.markdown("""
        <div class="info-box">
            <h3>📋 Como usar o sistema:</h3>
            <ol>
                <li>Clique no botão do módulo apropriado acima</li>
                <li>Escolha o usuário responsável pela petição</li>
                <li>Faça upload do arquivo com os dados</li>
                <li>Aguarde o processamento</li>
                <li>Baixe os arquivos gerados</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Módulo Novas CDAs
    elif modulo == "📝 Novas CDAs":
        st.header("📝 Geração de Petições para Novas CDAs")
        
        st.markdown("""
        <div class="info-box">
        Este módulo processa CDAs que ainda não foram ajuizadas. 
        O arquivo deve conter pelo menos uma coluna chamada 'cda' com os números das certidões.
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
        
        st.success(f"✅ Dados carregados: {len(da_merge):,} CDAs disponíveis")
        
        # Seleção de usuário
        st.subheader("1️⃣ Selecione o usuário responsável")
        usuarios = df_user['user'].tolist()
        usuario_selecionado = st.selectbox("Usuário:", usuarios)
        
        # Upload de arquivo
        st.subheader("2️⃣ Faça upload do arquivo")
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
                
                st.success(f"✅ Arquivo carregado: {len(df_input)} registros")
                
                # Preview dos dados
                with st.expander("👁️ Visualizar dados"):
                    st.dataframe(df_input.head(10))
                
                # Botão processar
                st.subheader("3️⃣ Processar petições")
                if st.button("🚀 Gerar Petições e Extratos", type="primary", key='processar_novas'):
                    peticoes, erros, df_merged = processar_modulo_novas_cdas(
                        df_input, da_merge, usuario_selecionado, df_user
                    )
                    
                    if peticoes:
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Processamento concluído!</h3>
                            <p><strong>{len(peticoes)}</strong> petições geradas com sucesso</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mostrar lista de CDAs processadas
                        with st.expander("📋 CDAs processadas"):
                            st.write(peticoes)
                        
                        # Download do Excel
                        if df_merged is not None:
                            st.download_button(
                                label="📥 Baixar dados consolidados (Excel)",
                                data=open('dados_retorno.xlsx', 'rb').read(),
                                file_name='dados_retorno.xlsx',
                                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                            )
                    
                    if erros:
                        st.error("⚠️ Erros encontrados:")
                        for erro in erros:
                            st.warning(erro)
            
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")
    
    # Módulo CDAs Ajuizadas
    elif modulo == "⚖️ CDAs Ajuizadas":
        st.header("⚖️ Geração de Petições para CDAs Ajuizadas")
        
        st.markdown("""
        <div class="info-box">
        Este módulo processa CDAs já ajuizadas em execuções fiscais. 
        O arquivo deve conter as colunas: 'cda', 'nome_executado' e 'numero_execucao'.
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
        
        st.success(f"✅ Dados carregados: {len(da_merge):,} CDAs disponíveis")
        
        # Seleção de usuário
        st.subheader("1️⃣ Selecione o usuário responsável")
        usuarios = df_user['user'].tolist()
        usuario_selecionado = st.selectbox("Usuário:", usuarios)
        
        # Upload de arquivo
        st.subheader("2️⃣ Faça upload do arquivo")
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
                    st.success(f"✅ Arquivo carregado: {len(df_input)} registros")
                    
                    # Preview dos dados
                    with st.expander("👁️ Visualizar dados"):
                        st.dataframe(df_input.head(10))
                    
                    # Botão processar
                    st.subheader("3️⃣ Processar petições")
                    if st.button("🚀 Gerar Petições e Extratos", type="primary", key='processar_ajuizadas'):
                        peticoes, erros, df_merged = processar_modulo_cdas_ajuizadas(
                            df_input, da_merge, usuario_selecionado, df_user
                        )
                        
                        if peticoes:
                            st.markdown(f"""
                            <div class="success-box">
                                <h3>✅ Processamento concluído!</h3>
                                <p><strong>{len(peticoes)}</strong> petições geradas com sucesso</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Mostrar lista de execuções processadas
                            with st.expander("📋 Execuções processadas"):
                                st.write(peticoes)
                            
                            # Download do Excel
                            if df_merged is not None:
                                st.download_button(
                                    label="📥 Baixar dados consolidados (Excel)",
                                    data=open('dados_retorno.xlsx', 'rb').read(),
                                    file_name='dados_retorno.xlsx',
                                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                )
                        
                        if erros:
                            st.error("⚠️ Erros encontrados:")
                            for erro in erros:
                                st.warning(erro)
            
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")

if __name__ == "__main__":
    main()