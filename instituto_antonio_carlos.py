import streamlit as st
import requests
import re
import csv
import pandas as pd
from datetime import datetime

# Funções auxiliares de validação e busca de endereço
def get_address_info(cep):
    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def validar_nome_completo(nome_completo):
    return re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$", nome_completo) and " " in nome_completo.strip()

def validar_cpf(cpf):
    return cpf.isnumeric() and len(cpf) == 11

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))

def validar_cep(cep):
    return cep.isnumeric() and len(cep) == 8

def validar_data_nascimento(data_nascimento):
    try:
        data = datetime.strptime(data_nascimento, '%d/%m/%Y')
        ano_atual = datetime.now().year
        return 1900 <= data.year <= 2024 and (ano_atual - data.year) >= 18
    except ValueError:
        return False

def salvar_dados_csv(dados):
    with open("cadastros.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(dados)

def atualizar_dados_csv(cpf, dados_atualizados):
    linhas = []
    with open("cadastros.csv", mode="r") as file:
        reader = csv.reader(file)
        for linha in reader:
            if linha[1] == cpf:
                linhas.append(dados_atualizados)
            else:
                linhas.append(linha)
    with open("cadastros.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(linhas)

def excluir_cadastro(cpf):
    linhas = []
    cpf_encontrado = False
    with open("cadastros.csv", mode="r") as file:
        reader = csv.reader(file)
        for linha in reader:
            if linha[1] != cpf:
                linhas.append(linha)
            else:
                cpf_encontrado = True
    if cpf_encontrado:
        with open("cadastros.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(linhas)
        return True
    else:
        return False

# Função de criar cadastro
def criar_cadastro():
    st.header("Criar Cadastro")
    nome_completo = st.text_input("Nome Completo (deve conter apenas letras e espaço para sobrenome)")
    cpf = st.text_input("CPF (apenas números, 11 dígitos)")
    email = st.text_input("Email")
    data_nascimento = st.text_input("Data de Nascimento (dd/mm/aaaa)")
    cep = st.text_input("CEP (apenas números, 8 dígitos)")

    cep_valido = False
    cidade, rua, bairro = "", "", ""
    if cep:
        if validar_cep(cep):
            endereco_info = get_address_info(cep)
            if endereco_info:
                cep_valido = True
                cidade = endereco_info.get("localidade", "")
                rua = endereco_info.get("logradouro", "")
                bairro = endereco_info.get("bairro", "")
                st.text_input("Cidade", cidade)
                st.text_input("Rua", rua)
                st.text_input("Bairro", bairro)
            else:
                st.error("CEP inválido ou não encontrado.")
        else:
            st.error("CEP deve conter apenas números e ter 8 dígitos.")

    numero = st.text_input("Número")
    complemento = st.text_input("Complemento")

    if st.button("Enviar"):
        erros = []
        if not validar_nome_completo(nome_completo):
            erros.append("Nome completo deve conter apenas letras e espaço para sobrenome.")
        if not validar_cpf(cpf):
            erros.append("CPF deve conter apenas números e ter 11 dígitos.")
        if not validar_email(email):
            erros.append("Email inválido.")
        if not validar_data_nascimento(data_nascimento):
            erros.append("Data de nascimento inválida ou você é menor de idade.")
        if not cep_valido:
            erros.append("CEP inválido ou não preenchido.")
        if not numero.isnumeric():
            erros.append("Número deve conter apenas números.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            dados = [nome_completo, cpf, email, data_nascimento, cep, cidade, rua, bairro, numero, complemento]
            salvar_dados_csv(dados)
            st.session_state["cadastrado"] = True
            st.success("Cadastro realizado com sucesso!")

# Função de visualizar alunos cadastrados
def visualizar_alunos():
    st.header("Alunos Cadastrados")
    try:
        df = pd.read_csv("cadastros.csv", header=None)
        if df.empty:
            st.warning("Nenhum aluno cadastrado encontrado.")
        else:
            df.columns = ["Nome Completo", "CPF", "Email", "Data de Nascimento", "CEP", "Cidade", "Rua", "Bairro", "Número", "Complemento"]
            st.dataframe(df)
    except FileNotFoundError:
        st.error("Nenhum aluno cadastrado encontrado.")
    except pd.errors.EmptyDataError:
        st.warning("O arquivo de cadastros está vazio.")

# Função de alterar cadastro
def alterar_cadastro():
    st.header("Alterar Cadastro")
    cpf = st.text_input("Digite o CPF do aluno para alterar (apenas números, 11 dígitos)")

    if "dados_aluno" not in st.session_state:
        st.session_state["dados_aluno"] = None

    buscar = st.button("Buscar")

    if buscar and validar_cpf(cpf):
        try:
            df = pd.read_csv("cadastros.csv", header=None)
            df.columns = ["Nome Completo", "CPF", "Email", "Data de Nascimento", "CEP", "Cidade", "Rua", "Bairro", "Número", "Complemento"]
            aluno = df[df["CPF"].astype(str) == cpf]
            if not aluno.empty:
                st.session_state["dados_aluno"] = aluno.iloc[0]
                st.write("Cadastro Encontrado:")
                st.write(aluno)
            else:
                st.error("CPF não encontrado.")
        except FileNotFoundError:
            st.error("Nenhum aluno cadastrado encontrado.")
        except pd.errors.EmptyDataError:
            st.warning("O arquivo de cadastros está vazio.")
    elif buscar:
        st.error("CPF inválido. Deve conter apenas números e ter 11 dígitos.")

    if st.session_state["dados_aluno"] is not None:
        dados_aluno = st.session_state["dados_aluno"]

        novo_nome = st.text_input("Novo Nome Completo", value=dados_aluno["Nome Completo"])
        nova_data_nascimento = st.text_input("Nova Data de Nascimento (dd/mm/aaaa)", value=dados_aluno["Data de Nascimento"])
        novo_email = st.text_input("Novo Email", value=dados_aluno["Email"])
        novo_cep = st.text_input("Novo CEP (apenas números, 8 dígitos)", value=dados_aluno["CEP"])
        novo_numero = st.text_input("Novo Número", value=dados_aluno["Número"])
        novo_complemento = st.text_input("Novo Complemento", value=dados_aluno["Complemento"])

        salvar = st.button("Salvar Alterações")

        if salvar:
            erros = []
            if novo_nome != dados_aluno["Nome Completo"] and not validar_nome_completo(novo_nome):
                erros.append("Nome completo deve conter apenas letras e espaço para sobrenome.")
            if nova_data_nascimento != dados_aluno["Data de Nascimento"] and not validar_data_nascimento(nova_data_nascimento):
                erros.append("Data de nascimento inválida ou você é menor de idade.")
            if novo_cep != dados_aluno["CEP"] and not validar_cep(novo_cep):
                erros.append("CEP deve conter apenas números e ter 8 dígitos.")
            if novo_email != dados_aluno["Email"] and not validar_email(novo_email):
                erros.append("Email inválido.")
            if novo_numero != dados_aluno["Número"] and not novo_numero.isnumeric():
                erros.append("Número deve conter apenas números.")

            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                if novo_cep != dados_aluno["CEP"]:
                    endereco_info = get_address_info(novo_cep)
                    if endereco_info:
                        cidade = endereco_info.get("localidade", "")
                        rua = endereco_info.get("logradouro", "")
                        bairro = endereco_info.get("bairro", "")
                    else:
                        st.error("CEP inválido ou não encontrado.")
                        return
                else:
                    cidade = dados_aluno["Cidade"]
                    rua = dados_aluno["Rua"]
                    bairro = dados_aluno["Bairro"]

                dados_atualizados = [novo_nome, cpf, novo_email, nova_data_nascimento, novo_cep, cidade, rua, bairro, novo_numero, novo_complemento]
                atualizar_dados_csv(cpf, dados_atualizados)
                st.success("Cadastro atualizado com sucesso!")
                st.session_state["dados_aluno"] = None  # Limpa os dados do aluno



# Função de excluir cadastro
def excluir_cadastro_view():
    st.header("Excluir Cadastro")
    cpf = st.text_input("Digite o CPF do aluno para excluir (apenas números, 11 dígitos)")
    if st.button("Excluir"):
        if validar_cpf(cpf):
            if excluir_cadastro(cpf):
                st.success("Cadastro excluído com sucesso!")
                st.experimental_rerun()  # Atualiza a página após excluir o cadastro
            else:
                st.error("CPF não encontrado.")
        else:
            st.error("CPF inválido. Deve conter apenas números e ter 11 dígitos.")

def exibir_cursos():
    st.header("Cursos Disponíveis")
    cursos = {
        "Saúde": {
            "Medicina": [
                "Anatomia Humana", "Fisiologia", "Farmacologia", "Patologia", "Clínica Médica", "Cirurgia Geral"
            ],
            "Odontologia": [
                "Anatomia Dentária", "Periodontia", "Endodontia", "Prótese Dentária", "Radiologia Odontológica", "Cirurgia Buco-maxilo-facial"
            ]
        },
        "Tecnologia": {
            "Análise e Desenvolvimento de Sistemas": [
                "Algoritmos e Programação", "Estrutura de Dados", "Desenvolvimento Web", "Banco de Dados", "Engenharia de Software", "Redes de Computadores"
            ]
        },
        "Ciências Humanas": {
            "Direito": [
                "Direito Constitucional", "Direito Penal", "Direito Civil", "Direito Empresarial", "Direito Trabalhista", "Direito Internacional"
            ],
            "Psicologia": [
                "Teorias da Personalidade", "Psicologia do Desenvolvimento", "Psicopatologia", "Psicologia Social", "Neuropsicologia", "Psicoterapia"
            ]
        },
        "Ciências Sociais": {
            "Administração": [
                "Introdução à Administração", "Marketing", "Gestão de Pessoas", "Contabilidade", "Finanças Empresariais", "Planejamento Estratégico"
            ]
        }
    }

    for area, cursos_area in cursos.items():
        with st.expander(f"Área: {area}"):
            for curso, aulas in cursos_area.items():
                if st.button(f"Curso: {curso}"):
                    st.write("**Aulas**:")
                    for aula in aulas:
                        st.write(f"- {aula}")

def main():
    st.title("Instituto Antonio Carlos")
    menu = ["Tela Inicial", "Criar Cadastro", "Visualizar Alunos", "Alterar Cadastro", "Excluir Cadastro", "Cursos Disponíveis", "Sair do App"]
    escolha = st.sidebar.selectbox("Menu", menu)

    if escolha == "Tela Inicial":
        st.subheader("Bem-vindo ao Instituto Antonio Carlos!")
        st.write(
            """
            O Instituto Antônio Carlos é uma iniciativa de Gabriel Borovina, Victor Sasaki e Felipe Gomes que nasceu com o objetivo de democratizar o acesso ao conhecimento de qualidade. Através de cursos EAD inovadores e personalizados, oferecemos aos estudantes as ferramentas e o suporte necessários para alcançar seus objetivos acadêmicos. Nosso compromisso é simplificar a jornada de aprendizado, proporcionando uma experiência flexível e eficaz.
            """
        )
        st.write("Selecione uma opção no menu ao lado para começar.")
    elif escolha == "Criar Cadastro":
        criar_cadastro()
    elif escolha == "Visualizar Alunos":
        visualizar_alunos()
    elif escolha == "Alterar Cadastro":
        alterar_cadastro()
    elif escolha == "Excluir Cadastro":
        excluir_cadastro_view()
    elif escolha == "Cursos Disponíveis":
        exibir_cursos()
    elif escolha == "Sair do App":
        st.subheader("Obrigado por escolher o Instituto Antonio Carlos!")
        st.stop()

if __name__ == '__main__':
    main()





