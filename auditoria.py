from datetime import datetime

from arquivos import adicionar_registro
from utils import formatar_data_hora

ARQUIVO_AUDITORIA = "auditoria.log"
CAMPOS_AUDITORIA = ["data_hora", "operacao", "matricula_afetada", "detalhe"]


def registrar_auditoria(operacao, matricula_afetada, detalhe=""):
    registro = {
        "data_hora": formatar_data_hora(datetime.now()),
        "operacao": operacao,
        "matricula_afetada": matricula_afetada,
        "detalhe": detalhe,
    }
    adicionar_registro(ARQUIVO_AUDITORIA, CAMPOS_AUDITORIA, registro)
