import os

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
SEPARADOR = ";"


def caminho(nome_arquivo):
    return os.path.join(PASTA_DADOS, nome_arquivo)


def garantir_arquivo(nome_arquivo, cabecalho=None):
    try:
        if not os.path.isdir(PASTA_DADOS):
            os.makedirs(PASTA_DADOS)
        if not os.path.exists(caminho(nome_arquivo)):
            with open(caminho(nome_arquivo), "w", encoding="utf-8") as arquivo:
                if cabecalho:
                    arquivo.write(SEPARADOR.join(cabecalho) + "\n")
    except OSError as erro:
        print(f"Erro ao criar o arquivo {nome_arquivo}: {erro}")


def ler_registros(nome_arquivo, cabecalho):
    garantir_arquivo(nome_arquivo, cabecalho)
    registros = []
    try:
        with open(caminho(nome_arquivo), "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()
    except OSError as erro:
        print(f"Erro ao ler o arquivo {nome_arquivo}: {erro}")
        return registros

    #linhas[0] é o cabeçalho os dados começam na linha 2 do arquivo
    for numero_linha in range(1, len(linhas)):
        linha = linhas[numero_linha].strip()
        if linha == "":
            continue
        campos = linha.split(SEPARADOR)
        if len(campos) != len(cabecalho):
            print(f"Aviso: a linha {numero_linha + 1} de {nome_arquivo} está mal formatada e foi ignorada.")
            continue
        registro = {}
        for i in range(len(cabecalho)):
            registro[cabecalho[i]] = campos[i]
        registros.append(registro)
    return registros


def montar_linha(cabecalho, registro):
    valores = []
    for campo in cabecalho:
        valores.append(str(registro[campo]))
    return SEPARADOR.join(valores) + "\n"


def salvar_registros(nome_arquivo, cabecalho, registros):
    try:
        with open(caminho(nome_arquivo), "w", encoding="utf-8") as arquivo:
            arquivo.write(SEPARADOR.join(cabecalho) + "\n")
            for registro in registros:
                arquivo.write(montar_linha(cabecalho, registro))
        return True
    except OSError as erro:
        print(f"Erro ao salvar o arquivo {nome_arquivo}: {erro}")
        return False


def adicionar_registro(nome_arquivo, cabecalho, registro):
    garantir_arquivo(nome_arquivo, cabecalho)
    try:
        with open(caminho(nome_arquivo), "a", encoding="utf-8") as arquivo:
            arquivo.write(montar_linha(cabecalho, registro))
        return True
    except OSError as erro:
        print(f"Erro ao gravar no arquivo {nome_arquivo}: {erro}")
        return False


def ler_lista_simples(nome_arquivo):
    garantir_arquivo(nome_arquivo)
    itens = []
    try:
        with open(caminho(nome_arquivo), "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha != "" and not linha.startswith("#"):
                    itens.append(linha.upper())
    except OSError as erro:
        print(f"Erro ao ler o arquivo {nome_arquivo}: {erro}")
    return itens
