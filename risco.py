# ##########################################################################
# ##                                                                      ##
# ##   >>> ARQUIVO RECRIADO EM 18/11 — Req. 2: Análise de risco  <<<      ##
# ##                                                                      ##
# ##   O QUE FOI FEITO:                                                   ##
# ##   O main.py e o acessos.py importavam "risco", mas o arquivo não     ##
# ##   estava na pasta do projeto, e o programa nem abria                 ##
# ##   (ModuleNotFoundError). Este arquivo foi refeito seguindo           ##
# ##   exatamente a tabela de critérios que está no README.               ##
# ##                                                                      ##
# ##   POR QUÊ:                                                           ##
# ##   Sem ele, nenhum acesso pode ser registrado nem classificado.       ##
# ##   Os pesos ficam em constantes aqui no topo para que o grupo possa   ##
# ##   ajustar as regras sem mexer na lógica.                             ##
# ##                                                                      ##
# ##########################################################################

from datetime import timedelta

from arquivos import ler_lista_simples
from usuarios import converter_horario
from utils import converter_data_hora

ARQUIVO_BLOQUEADAS = "bloqueadas.txt"

# Pesos de cada regra (ver tabela "Critérios de classificação" no README)
PONTOS_MAQUINA_BLOQUEADA = 3
PONTOS_FORA_DO_HORARIO = 2
PONTOS_LAB_FECHADO = 2
PONTOS_NAO_CADASTRADO = 2
PONTOS_FALHAS_REPETIDAS = 2
PONTOS_FALHA = 1
PONTOS_MAQUINA_DESCONHECIDA = 1

# Faixas de pontuação
LIMITE_SUSPEITO = 1   # 1 ou 2 pontos
LIMITE_CRITICO = 3    # 3 pontos ou mais

# Funcionamento do laboratório: das 7h às 22h
HORA_ABERTURA = 7
HORA_FECHAMENTO = 22

# Regra de tentativas repetidas
FALHAS_PARA_ALERTA = 3
JANELA_FALHAS = timedelta(hours=24)

TOTAL_MAQUINAS_LAB = 30


def carregar_bloqueadas():
    return ler_lista_simples(ARQUIVO_BLOQUEADAS)


def maquina_do_laboratorio(maquina):
    """True se a máquina segue o padrão LAB-01 até LAB-30."""
    if not maquina.startswith("LAB-"):
        return False
    numero = maquina[4:]
    if len(numero) != 2 or not numero.isdigit():
        return False
    return 1 <= int(numero) <= TOTAL_MAQUINAS_LAB


def fora_do_horario_permitido(usuario, data_hora):
    faixa = converter_horario(usuario["horario"])
    if faixa is None:
        # horário inválido no arquivo: tratamos como fora do horário, por segurança
        return True
    minutos = data_hora.hour * 60 + data_hora.minute
    inicio, fim = faixa
    return minutos < inicio or minutos >= fim


def laboratorio_fechado(data_hora):
    return data_hora.hour < HORA_ABERTURA or data_hora.hour >= HORA_FECHAMENTO


def contar_falhas_recentes(matricula, data_hora, acessos):
    """Conta as falhas da matrícula nas 24h anteriores a data_hora (sem contar o acesso atual)."""
    total = 0
    for acesso in acessos:
        if acesso["matricula"] != matricula or acesso["resultado"] != "falha":
            continue
        momento = converter_data_hora(acesso["data_hora"])
        if momento is None:
            continue
        diferenca = data_hora - momento
        if timedelta(0) <= diferenca <= JANELA_FALHAS:
            total += 1
    return total


def classificar_pontos(pontos):
    if pontos >= LIMITE_CRITICO:
        return "crítico"
    if pontos >= LIMITE_SUSPEITO:
        return "suspeito"
    return "normal"


def classificar_acesso(usuario, matricula, data_hora, maquina, resultado, acessos):
    """Aplica as regras e devolve (classificacao, pontos, lista_de_motivos)."""
    pontos = 0
    motivos = []

    if maquina in carregar_bloqueadas():
        pontos += PONTOS_MAQUINA_BLOQUEADA
        motivos.append(f"MÁQUINA BLOQUEADA: {maquina} está em bloqueadas.txt "
                       f"(+{PONTOS_MAQUINA_BLOQUEADA})")
    elif not maquina_do_laboratorio(maquina):
        pontos += PONTOS_MAQUINA_DESCONHECIDA
        motivos.append(f"Máquina {maquina} fora do padrão LAB-01 a LAB-{TOTAL_MAQUINAS_LAB} "
                       f"(+{PONTOS_MAQUINA_DESCONHECIDA})")

    if usuario is None:
        pontos += PONTOS_NAO_CADASTRADO
        motivos.append(f"Matrícula não cadastrada (+{PONTOS_NAO_CADASTRADO})")
    elif fora_do_horario_permitido(usuario, data_hora):
        pontos += PONTOS_FORA_DO_HORARIO
        motivos.append(f"Fora do horário permitido do usuário ({usuario['horario']}) "
                       f"(+{PONTOS_FORA_DO_HORARIO})")

    if laboratorio_fechado(data_hora):
        pontos += PONTOS_LAB_FECHADO
        motivos.append(f"Laboratório fechado (funciona das {HORA_ABERTURA}h às "
                       f"{HORA_FECHAMENTO}h) (+{PONTOS_LAB_FECHADO})")

    if resultado == "falha":
        pontos += PONTOS_FALHA
        motivos.append(f"Acesso com falha (+{PONTOS_FALHA})")
        falhas = contar_falhas_recentes(matricula, data_hora, acessos) + 1
        if falhas >= FALHAS_PARA_ALERTA:
            pontos += PONTOS_FALHAS_REPETIDAS
            motivos.append(f"{falhas} falhas desta matrícula nas últimas 24h "
                           f"(+{PONTOS_FALHAS_REPETIDAS})")

    if not motivos:
        motivos.append("Nenhuma regra de risco foi acionada")

    return classificar_pontos(pontos), pontos, motivos
