from arquivos import ler_registros, adicionar_registro
from auditoria import registrar_auditoria
from risco import classificar_acesso
from usuarios import carregar_usuarios, buscar_usuario, mascarar_matricula
from utils import (limpar_tela, pausar, ler_texto, ler_inteiro, ler_opcao,
                   ler_data_hora, formatar_data_hora)

ARQUIVO_ACESSOS = "acessos.csv"
CAMPOS_ACESSO = ["id", "matricula", "data_hora", "maquina", "resultado",
                 "classificacao", "pontos", "motivos"]
SEPARADOR_MOTIVOS = " | "
CLASSIFICACOES = ["normal", "suspeito", "crítico"]


def carregar_acessos():
    return ler_registros(ARQUIVO_ACESSOS, CAMPOS_ACESSO)


def proximo_id(acessos):
    maior = 0
    for acesso in acessos:
        try:
            numero = int(acesso["id"])
        except ValueError:
            continue
        if numero > maior:
            maior = numero
    return maior + 1


def ler_maquina():
    while True:
        maquina = ler_texto("Máquina de origem (ex.: LAB-07): ").upper()
        valida = len(maquina) <= 20
        for caractere in maquina:
            if not (caractere.isalnum() or caractere == "-"):
                valida = False
        if valida:
            return maquina
        print("Nome de máquina inválido: use letras, números e hífen (até 20 caracteres).")


def ler_resultado():
    print("Resultado: 1. Sucesso   2. Falha")
    if ler_inteiro("Resultado: ", 1, 2) == 1:
        return "sucesso"
    return "falha"


def mostrar_classificacao(classificacao, pontos, motivos):
    print()
    if classificacao == "crítico":
        print("!" * 60)
        print("  ALERTA: ACESSO CRÍTICO — verifique imediatamente")
        print("!" * 60)
    palavra = "ponto" if str(pontos) == "1" else "pontos"
    print(f"Classificação: {classificacao.upper()} ({pontos} {palavra})")
    print("Motivos:")
    for motivo in motivos:
        print(f"  - {motivo}")


#Registrar

def registrar_acesso():
    print(" Registrar acesso \n")
    usuarios = carregar_usuarios()
    acessos = carregar_acessos()

    matricula = ler_texto("Matrícula: ")
    usuario = buscar_usuario(matricula, usuarios)
    if usuario is None:
        print("Atenção: matrícula não cadastrada. O acesso será registrado como tentativa.")
    else:
        print(f"Usuário: {usuario['nome']} ({usuario['perfil']})")

    maquina = ler_maquina()
    resultado = ler_resultado()
    data_hora = ler_data_hora("Data e hora (dd/mm/aaaa hh:mm) ou Enter para agora: ")

    classificacao, pontos, motivos = classificar_acesso(
        usuario, matricula, data_hora, maquina, resultado, acessos)

    novo_acesso = {
        "id": proximo_id(acessos),
        "matricula": matricula,
        "data_hora": formatar_data_hora(data_hora),
        "maquina": maquina,
        "resultado": resultado,
        "classificacao": classificacao,
        "pontos": pontos,
        "motivos": SEPARADOR_MOTIVOS.join(motivos),
    }
    if adicionar_registro(ARQUIVO_ACESSOS, CAMPOS_ACESSO, novo_acesso):
        registrar_auditoria("REGISTRAR_ACESSO", matricula,
                            f"acesso {novo_acesso['id']} classificado como {classificacao}")
        print(f"\nAcesso nº {novo_acesso['id']} registrado.")
        mostrar_classificacao(classificacao, pontos, motivos)


#Consultar

def imprimir_tabela_acessos(acessos):
    if not acessos:
        print("Nenhum acesso encontrado.")
        return
    print(f"{'ID':<5}{'Data e hora':<18}{'Matrícula':<13}{'Máquina':<14}{'Resultado':<11}Classificação")
    print("-" * 75)
    for acesso in acessos:
        print(f"{acesso['id']:<5}{acesso['data_hora']:<18}{mascarar_matricula(acesso['matricula']):<13}"
              f"{acesso['maquina'][:13]:<14}{acesso['resultado']:<11}{acesso['classificacao']}")
    print(f"\nTotal: {len(acessos)} acesso(s)")


def listar_todos_acessos():
    print(" Todos os acessos \n")
    imprimir_tabela_acessos(carregar_acessos())


def consultar_por_matricula():
    print(" Acessos por matrícula \n")
    matricula = ler_texto("Matrícula: ")
    encontrados = []
    for acesso in carregar_acessos():
        if acesso["matricula"] == matricula:
            encontrados.append(acesso)
    print()
    imprimir_tabela_acessos(encontrados)


def consultar_por_classificacao():
    print(" Acessos por classificação \n")
    print("1. Normal   2. Suspeito   3. Crítico")
    escolhida = CLASSIFICACOES[ler_inteiro("Classificação: ", 1, 3) - 1]
    encontrados = []
    for acesso in carregar_acessos():
        if acesso["classificacao"] == escolhida:
            encontrados.append(acesso)
    print()
    imprimir_tabela_acessos(encontrados)


def ver_detalhes_acesso():
    print(" Detalhes de um acesso \n")
    acessos = carregar_acessos()
    if not acessos:
        print("Nenhum acesso registrado.")
        return
    id_procurado = str(ler_inteiro("ID do acesso: ", 1, proximo_id(acessos) - 1))
    for acesso in acessos:
        if acesso["id"] == id_procurado:
            print(f"\nAcesso nº {acesso['id']}")
            print(f"Matrícula: {mascarar_matricula(acesso['matricula'])}")
            print(f"Data e hora: {acesso['data_hora']}")
            print(f"Máquina: {acesso['maquina']}")
            print(f"Resultado: {acesso['resultado']}")
            mostrar_classificacao(acesso["classificacao"], acesso["pontos"],
                                  acesso["motivos"].split(SEPARADOR_MOTIVOS))
            return
    print("Acesso não encontrado.")


def menu_acessos():
    acoes = {
        "1": registrar_acesso,
        "2": listar_todos_acessos,
        "3": consultar_por_matricula,
        "4": consultar_por_classificacao,
        "5": ver_detalhes_acesso,
    }
    while True:
        limpar_tela()
        print(" ACESSOS ")
        print("1. Registrar acesso")
        print("2. Listar todos os acessos")
        print("3. Consultar por matrícula")
        print("4. Consultar por classificação")
        print("5. Ver detalhes e motivos de um acesso")
        print("0. Voltar")
        print("\n(Acessos não podem ser editados nem excluídos.)")
        opcao = ler_opcao("\nEscolha: ", ["0", "1", "2", "3", "4", "5"])
        if opcao == "0":
            return
        limpar_tela()
        acoes[opcao]()
        pausar()
