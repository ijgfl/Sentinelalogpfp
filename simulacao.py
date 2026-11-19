# ##########################################################################
# ##                                                                      ##
# ##   >>> NOVO EM 18/11 — Req. 7: Funcionalidade extra                   ##
# ##       Modo de simulação de acessos aleatórios                        ##
# ##                                                                      ##
# ##   O QUE FOI FEITO:                                                   ##
# ##   Opção 6 do menu principal. Gera N acessos aleatórios (usando a     ##
# ##   biblioteca random, permitida no enunciado) nos últimos 7 dias,     ##
# ##   passa cada um pelas MESMAS regras de risco.py e mostra o           ##
# ##   resultado. Há dois modos:                                          ##
# ##     1. Só testar: mostra as classificações e NÃO grava nada.         ##
# ##     2. Gravar: salva os acessos em acessos.csv (com confirmação).    ##
# ##                                                                      ##
# ##   POR QUÊ:                                                           ##
# ##   - Serve para testar as regras com muitos casos de uma vez e para   ##
# ##     ter dados no relatório e nas máquinas compartilhadas na demo.    ##
# ##   - A simulação "puxa" de propósito alguns casos perigosos (madru-   ##
# ##     gada, máquina bloqueada, matrícula inexistente, falhas), senão   ##
# ##     quase tudo sairia normal e as regras não seriam testadas.        ##
# ##   - Acessos não podem ser apagados (Req. 1). Por isso o modo padrão  ##
# ##     é "só testar", a gravação pede confirmação e fica na auditoria   ##
# ##     com os IDs gerados — assim dá para saber quais são simulados.    ##
# ##                                                                      ##
# ##########################################################################

import random
from datetime import datetime, timedelta

from acessos import (carregar_acessos, proximo_id, mostrar_classificacao,
                     ARQUIVO_ACESSOS, CAMPOS_ACESSO, SEPARADOR_MOTIVOS)
from arquivos import adicionar_registro
from auditoria import registrar_auditoria
from risco import classificar_acesso, carregar_bloqueadas, TOTAL_MAQUINAS_LAB
from usuarios import carregar_usuarios, buscar_usuario, mascarar_matricula
from utils import formatar_data_hora, ler_inteiro, ler_sim_nao

MAXIMO_SIMULADOS = 50
DIAS_PARA_TRAS = 7

# Probabilidades usadas no sorteio (ajustáveis)
CHANCE_FALHA = 0.25
CHANCE_MADRUGADA = 0.10
CHANCE_MAQUINA_BLOQUEADA = 0.05
CHANCE_MAQUINA_DESCONHECIDA = 0.05
CHANCE_NAO_CADASTRADO = 0.08


def sortear_matricula(usuarios):
    if not usuarios or random.random() < CHANCE_NAO_CADASTRADO:
        return "SIM" + str(random.randint(1000, 9999))   # matrícula inexistente
    return random.choice(usuarios)["matricula"]


def sortear_maquina(bloqueadas):
    sorteio = random.random()
    if bloqueadas and sorteio < CHANCE_MAQUINA_BLOQUEADA:
        return random.choice(bloqueadas)
    if sorteio < CHANCE_MAQUINA_BLOQUEADA + CHANCE_MAQUINA_DESCONHECIDA:
        return "PC-" + str(random.randint(100, 999))
    return f"LAB-{random.randint(1, TOTAL_MAQUINAS_LAB):02d}"


def sortear_data_hora():
    agora = datetime.now().replace(second=0, microsecond=0)
    dia = agora - timedelta(days=random.randint(0, DIAS_PARA_TRAS))
    if random.random() < CHANCE_MADRUGADA:
        hora = random.randint(0, 5)
    else:
        hora = random.randint(7, 21)
    momento = dia.replace(hour=hora, minute=random.randint(0, 59))
    if momento > agora:
        # não pode haver acesso no futuro: joga para o dia anterior
        momento -= timedelta(days=1)
    return momento


def sortear_resultado():
    return "falha" if random.random() < CHANCE_FALHA else "sucesso"


def gerar_acessos(quantidade):
    """Gera e classifica os acessos. Não grava nada no arquivo."""
    usuarios = carregar_usuarios()
    bloqueadas = carregar_bloqueadas()
    historico = carregar_acessos()   # a regra de falhas em 24h olha o histórico
    novo_id = proximo_id(historico)

    momentos = sorted(sortear_data_hora() for _ in range(quantidade))
    gerados = []
    for momento in momentos:
        matricula = sortear_matricula(usuarios)
        maquina = sortear_maquina(bloqueadas)
        resultado = sortear_resultado()
        classificacao, pontos, motivos = classificar_acesso(
            buscar_usuario(matricula, usuarios), matricula, momento,
            maquina, resultado, historico)
        acesso = {
            "id": novo_id,
            "matricula": matricula,
            "data_hora": formatar_data_hora(momento),
            "maquina": maquina,
            "resultado": resultado,
            "classificacao": classificacao,
            "pontos": pontos,
            "motivos": SEPARADOR_MOTIVOS.join(motivos),
        }
        gerados.append(acesso)
        historico.append(acesso)   # o próximo sorteado já "enxerga" este
        novo_id += 1
    return gerados


def mostrar_resumo(gerados):
    contagem = {"normal": 0, "suspeito": 0, "crítico": 0}
    print(f"\n{'ID':<5}{'Data e hora':<18}{'Matrícula':<13}{'Máquina':<20}{'Resultado':<11}Classificação")
    print("-" * 80)
    for acesso in gerados:
        contagem[acesso["classificacao"]] += 1
        print(f"{acesso['id']:<5}{acesso['data_hora']:<18}{mascarar_matricula(acesso['matricula']):<13}"
              f"{acesso['maquina']:<20}{acesso['resultado']:<11}{acesso['classificacao']}")
    print(f"\nNormais: {contagem['normal']}   Suspeitos: {contagem['suspeito']}   "
          f"Críticos: {contagem['crítico']}")


def gravar_acessos(gerados):
    gravados = 0
    for acesso in gerados:
        if adicionar_registro(ARQUIVO_ACESSOS, CAMPOS_ACESSO, acesso):
            gravados += 1
    if gravados:
        registrar_auditoria("SIMULAR_ACESSOS", "-",
                            f"{gravados} acessos simulados (IDs {gerados[0]['id']} a {gerados[-1]['id']})")
    print(f"{gravados} acesso(s) simulado(s) gravado(s).")


def menu_simulacao():
    print(" SIMULAÇÃO DE ACESSOS ALEATÓRIOS \n")
    print("Gera acessos fictícios e aplica as mesmas regras de risco do sistema.")
    if not carregar_usuarios():
        print("Aviso: nenhum usuário cadastrado; todos os acessos serão de matrículas inexistentes.")
    quantidade = ler_inteiro(f"\nQuantos acessos gerar (1 a {MAXIMO_SIMULADOS})? ", 1, MAXIMO_SIMULADOS)
    gerados = gerar_acessos(quantidade)
    mostrar_resumo(gerados)

    if ler_sim_nao("\nVer os motivos de um acesso gerado? (s/n): "):
        primeiro = int(gerados[0]["id"])
        escolhido = gerados[ler_inteiro("ID: ", primeiro, primeiro + len(gerados) - 1) - primeiro]
        mostrar_classificacao(escolhido["classificacao"], escolhido["pontos"],
                              escolhido["motivos"].split(SEPARADOR_MOTIVOS))

    print("\nATENÇÃO: acessos gravados não podem ser editados nem excluídos depois.")
    if ler_sim_nao("Gravar estes acessos em acessos.csv? (s/n): "):
        gravar_acessos(gerados)
    else:
        print("Nada foi gravado (modo só testar).")
