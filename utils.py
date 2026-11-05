import os
from datetime import datetime

FORMATO_DATA_HORA = "%d/%m/%Y %H:%M"


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\nPressione Enter para continuar...")


def sanitizar(texto):
    return texto.replace(";", ",").replace("\n", " ").replace("\r", " ").strip()


def ler_texto(mensagem, obrigatorio=True):
    while True:
        texto = sanitizar(input(mensagem))
        if texto or not obrigatorio:
            return texto
        print("Este campo não pode ficar vazio.")


def ler_inteiro(mensagem, minimo, maximo):
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro.")
            continue
        if valor < minimo or valor > maximo:
            print(f"Digite um valor entre {minimo} e {maximo}.")
            continue
        return valor


def ler_opcao(mensagem, opcoes_validas):
    while True:
        opcao = input(mensagem).strip()
        if opcao in opcoes_validas:
            return opcao
        print("Opção inválida.")


def ler_sim_nao(mensagem):
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in ["s", "sim"]:
            return True
        if resposta in ["n", "nao", "não"]:
            return False
        print("Responda com s ou n.")


def converter_data_hora(texto):
    try:
        return datetime.strptime(texto.strip(), FORMATO_DATA_HORA)
    except ValueError:
        return None


def formatar_data_hora(data_hora):
    return data_hora.strftime(FORMATO_DATA_HORA)


def ler_data_hora(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto == "":
            return datetime.now().replace(second=0, microsecond=0)
        data_hora = converter_data_hora(texto)
        if data_hora is None:
            print("Formato inválido. Use dd/mm/aaaa hh:mm (ex.: 03/11/2026 14:30).")
        elif data_hora > datetime.now():
            print("Não é possível registrar um acesso no futuro.")
        else:
            return data_hora
