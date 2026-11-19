# ##########################################################################
# ##                                                                      ##
# ##   >>> NOVO EM 18/11 — Req. 4: Consulta do log de auditoria pelo menu ##
# ##                                                                      ##
# ##   O QUE FOI FEITO:                                                   ##
# ##   Opção 4 do menu principal. Lista o auditoria.log (data, operação,  ##
# ##   matrícula MASCARADA e detalhe), com filtro por tipo de operação.   ##
# ##                                                                      ##
# ##   POR QUÊ:                                                           ##
# ##   O enunciado pede que o log possa ser consultado pelo menu. A       ##
# ##   gravação já existia em auditoria.py; faltava a leitura.            ##
# ##   Ficou num arquivo separado porque usuarios.py importa auditoria.py;##
# ##   se auditoria.py importasse usuarios.py (para mascarar a matrícula) ##
# ##   haveria importação circular.                                       ##
# ##   Consultar o log também é registrado: quem olha os rastros dos      ##
# ##   outros também deixa o próprio rastro.                              ##
# ##                                                                      ##
# ##########################################################################

from arquivos import ler_registros
from auditoria import ARQUIVO_AUDITORIA, CAMPOS_AUDITORIA, registrar_auditoria
from usuarios import mascarar_matricula
from utils import limpar_tela, pausar, ler_opcao, ler_inteiro

QUANTIDADE_RECENTES = 30


def carregar_auditoria():
    return ler_registros(ARQUIVO_AUDITORIA, CAMPOS_AUDITORIA)


def mascarar_se_matricula(valor):
    # operações sem usuário afetado (ex.: CONSULTAR_IA) gravam "-"
    if valor in ("", "-"):
        return "-"
    return mascarar_matricula(valor)


def imprimir_tabela_auditoria(registros):
    if not registros:
        print("Nenhum registro encontrado.")
        return
    print(f"{'Data e hora':<18}{'Operação':<22}{'Matrícula':<13}Detalhe")
    print("-" * 80)
    for registro in registros:
        print(f"{registro['data_hora']:<18}{registro['operacao'][:21]:<22}"
              f"{mascarar_se_matricula(registro['matricula_afetada']):<13}"
              f"{registro['detalhe'][:50]}")
    print(f"\nTotal: {len(registros)} registro(s)")


def listar_recentes():
    print(f" Últimos {QUANTIDADE_RECENTES} registros \n")
    imprimir_tabela_auditoria(carregar_auditoria()[-QUANTIDADE_RECENTES:])


def listar_todos():
    print(" Log de auditoria completo \n")
    imprimir_tabela_auditoria(carregar_auditoria())


def filtrar_por_operacao():
    print(" Filtrar por operação \n")
    registros = carregar_auditoria()
    operacoes = sorted(set(registro["operacao"] for registro in registros))
    if not operacoes:
        print("O log de auditoria está vazio.")
        return
    for numero, operacao in enumerate(operacoes, start=1):
        print(f"{numero}. {operacao}")
    escolhida = operacoes[ler_inteiro("\nOperação: ", 1, len(operacoes)) - 1]
    encontrados = [registro for registro in registros if registro["operacao"] == escolhida]
    print()
    imprimir_tabela_auditoria(encontrados)


def menu_auditoria():
    acoes = {
        "1": listar_recentes,
        "2": listar_todos,
        "3": filtrar_por_operacao,
    }
    while True:
        limpar_tela()
        print(" LOG DE AUDITORIA ")
        print(f"1. Ver os {QUANTIDADE_RECENTES} registros mais recentes")
        print("2. Ver o log completo")
        print("3. Filtrar por operação")
        print("0. Voltar")
        opcao = ler_opcao("\nEscolha: ", ["0", "1", "2", "3"])
        if opcao == "0":
            return
        limpar_tela()
        acoes[opcao]()
        registrar_auditoria("CONSULTAR_AUDITORIA", "-", f"opção {opcao} do menu de auditoria")
        pausar()
