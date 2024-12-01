import streamlit as st
import requests
import re
import csv
import pandas as pd

def get_address_info(cep):
    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def validar_nome(nome):
    if not re.match("^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$", nome):
        return False
    if " " not in nome.strip():
        return False
    return True

def validar_cpf(cpf):
    return cpf.isnumeric() and len(cpf) == 11

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(padrao, email):
        return True
    return False

def validar_cep(cep):
    return cep.isnumeric() and len(cep) == 8

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

def criar_cadastro():
    st.header("Criar Cadastro")
    nome = st.text_input("Nome (deve conter apenas letras e espaço para sobrenome)")
    cpf = st.text_input("CPF (apenas números, 11 dígitos)")
    nome_completo = st.text_input("Nome Completo")
    email = st.text_input("Email")
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

    complemento = st.text_input("Complemento")
    
    if st.button("Enviar"):
        erros = []
        if not validar_nome(nome):
            erros.append("Nome deve conter apenas letras e espaço para sobrenome.")
        if not validar_cpf(cpf):
            erros.append("CPF deve conter apenas números e ter 11 dígitos.")
        if not validar_email(email):
            erros.append("Email inválido.")
        if not cep_valido:
            erros.append("CEP inválido ou não preenchido.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            dados = [nome, cpf, nome_completo, email, cep, cidade, rua, bairro, complemento]
            salvar_dados_csv(dados)
            st.success("Cadastro realizado com sucesso!")

def visualizar_alunos():
    st.header("Alunos Cadastrados")
    try:
        df = pd.read_csv("cadastros.csv", header=None)
        df.columns = ["Nome", "CPF", "Nome Completo", "Email", "CEP", "Cidade", "Rua", "Bairro", "Complemento"]
        st.dataframe(df)
    except FileNotFoundError:
        st.error("Nenhum aluno cadastrado encontrado.")

def alterar_cadastro():
    st.header("Alterar Cadastro")
    cpf = st.text_input("Digite o CPF do aluno para alterar (apenas números, 11 dígitos)")
    if validar_cpf(cpf):
        if st.button("Buscar"):
            try:
                df = pd.read_csv("cadastros.csv", header=None)
                df.columns = ["Nome", "CPF", "Nome Completo", "Email", "CEP", "Cidade", "Rua", "Bairro", "Complemento"]
                aluno = df[df["CPF"] == cpf]
                if not aluno.empty:
                    st.write("Cadastro Encontrado:")
                    st.write(aluno)
                    novo_cep = st.text_input("Novo CEP (apenas números, 8 dígitos)", value=aluno["CEP"].values[0])
                    novo_email = st.text_input("Novo Email", value=aluno["Email"].values[0])
                    if st.button("Salvar Alterações"):
                        if validar_cep(novo_cep) and validar_email(novo_email):
                            endereco_info = get_address_info(novo_cep)
                            if endereco_info:
                                cidade = endereco_info.get("localidade", "")
                                rua = endereco_info.get("logradouro", "")
                                bairro = endereco_info.get("bairro", "")
                                dados_atualizados = [aluno["Nome"].values[0], cpf, aluno["Nome Completo"].values[0], novo_email, novo_cep, cidade, rua, bairro, aluno["Complemento"].values[0]]
                                atualizar_dados_csv(cpf, dados_atualizados)
                                st.success("Cadastro atualizado com sucesso!")
                            else:
                                st.error("Novo CEP inválido ou não encontrado.")
                        else:
                            st.error("Dados inválidos. Verifique o CEP e o email.")
                else:
                    st.error("CPF não encontrado.")
            except FileNotFoundError:
                st.error("Nenhum aluno cadastrado encontrado.")
    else:
        if st.button("Buscar"):
            st.error("CPF inválido. Deve conter apenas números e ter 11 dígitos.")

def exibir_cursos():
    st.header("Cursos Disponíveis")
    cursos = {
        "Medicina": {
            "Duração": "6 anos",
            "Área": "Saúde",
            "Aulas": [
                "Anatomia Humana", "Fisiologia", "Farmacologia", "Patologia", "Clínica Médica", "Cirurgia Geral"
            ]
        },
        "Análise e Desenvolvimento de Sistemas": {
            "Duração": "3 anos",
            "Área": "Tecnologia",
            "Aulas": [
                "Algoritmos e Programação", "Estrutura de Dados", "Desenvolvimento Web", "Banco de Dados", "Engenharia de Software", "Redes de Computadores"
            ]
        },
        "Direito": {
            "Duração": "5 anos",
            "Área": "Ciências Humanas",
            "Aulas": [
                "Direito Constitucional", "Direito Penal", "Direito Civil", "Direito Empresarial", "Direito Trabalhista", "Direito Internacional"
            ]
        },
        "Administração": {
            "Duração": "4 anos",
            "Área": "Ciências Sociais",
            "Aulas": [
                "Introdução à Administração", "Marketing", "Gestão de Pessoas", "Contabilidade", "Finanças Empresariais", "Planejamento Estratégico"
            ]
        },
        "Odontologia": {
            "Duração": "5 anos",
            "Área": "Saúde",
            "Aulas": [
                "Anatomia Dentária", "Periodontia", "Endodontia", "Prótese Dentária", "Radiologia Odontológica", "Cirurgia Buco-maxilo-facial"
            ]
        },
        "Psicologia": {
            "Duração": "5 anos",
            "Área": "Ciências Humanas",
            "Aulas": [
                "Teorias da Personalidade", "Psicologia do Desenvolvimento", "Psicopatologia", "Psicologia Social", "Neuropsicologia", "Psicoterapia"
            ]
        }
    }
    
    curso_escolhido = st.selectbox("Escolha um curso", list(cursos.keys()))
    if curso_escolhido:
        curso_info = cursos[curso_escolhido]
        st.subheader(f"CURSO: {curso_escolhido}")
        st.write(f"**Duração**: {curso_info['Duração']}")
        st.write(f"**Área**: {curso_info['Área']}")
        st.write("**Aulas**:")
        for aula in curso_info["Aulas"]:
            st.write(f"- {aula}")

def main():
    st.title("INSTITUTO ANTONIO CARLOS")
    menu = ["Início", "Criar Cadastro", "Aluno Existente", "Alterar Cadastro", "Acessar Cursos", "Sair"]
    escolha = st.sidebar.selectbox("Menu", menu)

    if escolha == "Início":
        st.subheader("Bem-vindo ao Instituto Antonio Carlos!")
    elif escolha == "Criar Cadastro":
        criar_cadastro()
    elif escolha == "Aluno Existente":
        visualizar_alunos()
    elif escolha == "Alterar Cadastro":
        alterar_cadastro()
    elif escolha == "Acessar Cursos":
        exibir_cursos()
    elif escolha == "Sair
