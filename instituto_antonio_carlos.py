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

def validar_nome_completo(nome_completo):
    return re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$", nome_completo) and " " in nome_completo.strip()

def validar_cpf(cpf):
    return cpf.isnumeric() and len(cpf) == 11

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))

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

def excluir_cadastro(cpf):
    linhas = []
    with open("cadastros.csv", mode="r") as file:
        reader = csv.reader(file)
        for linha in reader:
            if linha[1] != cpf:
                linhas.append(linha)
    with open("cadastros.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(linhas)

def criar_cadastro():
    st.header("Criar Cadastro")
    nome_completo = st.text_input("Nome Completo (deve conter apenas letras e espaço para sobrenome)")
    cpf = st.text_input("CPF (apenas números, 11 dígitos)")
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
        if not cep_valido:
            erros.append("CEP inválido ou não preenchido.")
        if not numero.isnumeric():
            erros.append("Número deve conter apenas números.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            dados = [nome_completo, cpf, email, cep, cidade, rua, bairro, numero, complemento]
            salvar_dados_csv(dados)
            st.session_state["cadastrado"] = True
            st.success("Cadastro realizado com sucesso!")

def visualizar_alunos():
    st.header("Alunos Cadastrados")
    try:
        df = pd.read_csv("cadastros.csv", header=None)
        df.columns = ["Nome Completo", "CPF", "Email", "CEP", "Cidade", "Rua", "Bairro", "Número", "Complemento"]
        st.dataframe(df)
    except FileNotFoundError:
        st.error("Nenhum aluno cadastrado encontrado.")

def alterar_cadastro():
    st.header("Alterar Cadastro")
    cpf = st.text_input("Digite o CPF do aluno para alterar ou excluir (apenas números, 11 dígitos)")
    if validar_cpf(cpf):
        if st.button("Buscar"):
            try:
                df = pd.read_csv("cadastros.csv", header=None)
                df.columns = ["Nome Completo", "CPF", "Email", "CEP", "Cidade", "Rua", "Bairro", "Número", "Complemento"]
                aluno = df[df["CPF"] == cpf]
                if not aluno.empty:
                    st.write("Cadastro Encontrado:")
                    st.write(aluno)
                    novo_cep = st.text_input("Novo CEP (apenas números, 8 dígitos)", value=aluno["CEP"].values[0])
                    novo_email = st.text_input("Novo Email", value=aluno["Email"].values[0])
                    novo_numero = st.text_input("Novo Número", value=aluno["Número"].values[0])
                    novo_complemento = st.text_input("Novo Complemento", value=aluno["Complemento"].values[0])
                    if st.button("Salvar Alterações"):
                        if validar_cep(novo_cep) and validar_email(novo_email) and novo_numero.isnumeric():
                            endereco_info = get_address_info(novo_cep)
                            if endereco_info:
                                cidade = endereco_info.get("localidade", "")
                                rua = endereco_info.get("logradouro", "")
                                bairro = endereco_info.get("bairro", "")
                                dados_atualizados = [aluno["Nome Completo"].values[0], cpf, novo_email, novo_cep, cidade, rua, bairro, novo_numero, novo_complemento]
                                atualizar_dados_csv(cpf, dados_atualizados)
                                st.success("Cadastro atualizado com sucesso!")
                        else:
                            st.error("Dados inválidos. Verifique o CEP, o email e o número.")
                    if st.button("Excluir Cadastro"):
                        excluir_cadastro(cpf)
                        st.success("Cadastro excluído com sucesso!")
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
                with st.expander(f"Curso: {curso}"):
                    st.write("**Aulas**:")
                    for aula in aulas:
                        st.button(aula)

def main():
    st.title("INSTITUTO ANTONIO CARLOS")
    st.subheader("O Instituto Antônio Carlos é uma iniciativa de Gabriel Borovina, Victor Sasaki e Felipe Gomes que nasceu com o objetivo de democratizar o acesso ao conhecimento de qualidade. Através de cursos EAD inovadores e personalizados, oferecemos aos estudantes as ferramentas e o suporte necessários para alcançar seus objetivos acadêmicos. Nosso compromisso é simplificar a jornada de aprendizado, proporcionando uma experiência flexível e eficaz.")

    menu = ["Início", "Criar Cadastro", "Aluno Existente", "Alterar Cadastro", "Acessar Cursos", "Sair"]


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
        if st.session_state.get("cadastrado", False):
            exibir_cursos()
        else:
            st.warning("Por favor, realize o cadastro primeiro para acessar os cursos.")
    elif escolha == "Sair":
        st.subheader("Obrigado por usar o sistema!")
        st.stop()

if __name__ == "__main__":
    main()




