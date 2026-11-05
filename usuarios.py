"""feito por karla e corrigido pelo claude"""
from arquivos import ler_registros, salvar_registros
from auditoria import registrar_auditoria

ARQUIVO_USUARIOS = "usuarios.csv"
CAMPOS_USUARIO = ["matricula", "nome", "perfil", "horario", "observacoes"]

PERFIS = {
    "1": "Estudante",
    "2": "Professor",
    "3": "Administrador"
}



def salvar_usuarios(usuarios):
    # a gravação usa o arquivos.py, igual aos outros módulos (pasta dados/, utf-8)
    if not salvar_registros(ARQUIVO_USUARIOS, CAMPOS_USUARIO, usuarios):
        print("Erro ao salvar os usuários.")
        return False
    return True



def carregar_usuarios():
    return ler_registros(ARQUIVO_USUARIOS, CAMPOS_USUARIO)



def buscar_usuario(matricula, usuarios):

    for usuario in usuarios:

        if usuario["matricula"] == matricula:
            return usuario

    return None



def mascarar_matricula(matricula):

    return matricula[:2] + "*" * max(4, len(matricula) - 2)



def converter_horario(horario):
    """Transforma '08:00-18:00' em (480, 1080), em minutos. Devolve None se for inválido."""

    try:
        partes = horario.split("-")

        if len(partes) != 2:
            return None

        minutos = []

        for parte in partes:
            hora_minuto = parte.split(":")

            if len(hora_minuto) != 2:
                return None

            hora = int(hora_minuto[0])
            minuto = int(hora_minuto[1])

            if hora < 0 or hora > 23:
                return None

            if minuto < 0 or minuto > 59:
                return None

            minutos.append(hora * 60 + minuto)

        return minutos[0], minutos[1]

    except ValueError:
        return None



def validar_horario(horario):

    faixa = converter_horario(horario)

    if faixa is None:
        return False

    # o horário final precisa ser depois do inicial
    return faixa[1] > faixa[0]



def validar_matricula(matricula):

    return matricula.isalnum() and len(matricula) >= 4



def validar_nome(nome):
    """Só letras, espaço, hífen e apóstrofo: evita texto que pareça instrução para a IA."""

    if len(nome) < 2 or len(nome) > 60:
        return False

    for caractere in nome:
        if not (caractere.isalpha() or caractere in " -'"):
            return False

    return True



def escolher_usuario(usuarios):
    """Mostra a lista numerada (com matrícula mascarada) e devolve o usuário escolhido.

    A escolha é pelo número, porque a matrícula fica escondida na listagem.
    """

    listar_usuarios(usuarios)

    if len(usuarios) == 0:
        return None

    try:
        numero = int(input("\nNúmero do usuário (0 para cancelar): "))
    except ValueError:
        print("Digite um número.")
        return None

    if numero < 1 or numero > len(usuarios):
        if numero != 0:
            print("Número inválido.")
        return None

    return usuarios[numero - 1]




def cadastrar_usuario(usuarios):

    print("\n--- CADASTRAR USUÁRIO ---")

    nome = input("Nome: ").strip()
    matricula = input("Matrícula: ").strip()

    if not nome or not matricula:
        print("Nome e matrícula são obrigatórios.")
        return

    if not validar_nome(nome):
        print("Nome inválido: use só letras, espaço, hífen ou apóstrofo (2 a 60 caracteres).")
        return

    if not validar_matricula(matricula):
        print("Matrícula inválida: use só letras e números, com pelo menos 4 caracteres.")
        return

    if buscar_usuario(matricula, usuarios) is not None:
        print("Esta matrícula já está cadastrada.")
        return

    print("\n1 - Estudante")
    print("2 - Professor")
    print("3 - Administrador")

    opcao = input("Escolha o perfil: ")

    if opcao not in PERFIS:
        print("Perfil inválido.")
        return

    horario = input("Horário permitido (08:00-18:00): ").strip()

    if not validar_horario(horario):
        print("Formato de horário inválido.")
        return

    observacoes = input("Observações: ").strip()

    if ";" in observacoes:
        print("Não utilize ponto e vírgula nos campos.")
        return

    usuario = {
        "nome": nome,
        "matricula": matricula,
        "perfil": PERFIS[opcao],
        "horario": horario,
        "observacoes": observacoes
    }

    usuarios.append(usuario)

    if salvar_usuarios(usuarios):
        registrar_auditoria("CADASTRAR_USUARIO", matricula, "perfil " + PERFIS[opcao])
        print("Usuário cadastrado com sucesso!")



def listar_usuarios(usuarios):

    print("\n--- LISTA DE USUÁRIOS ---")

    if len(usuarios) == 0:
        print("Nenhum usuário cadastrado.")
        return

    numero = 1

    for usuario in usuarios:

        # a listagem SEMPRE mostra a matrícula mascarada
        print("--------------------------")
        print("Nº:", numero)
        print("Nome:", usuario["nome"])
        print("Matrícula:", mascarar_matricula(usuario["matricula"]))
        print("Perfil:", usuario["perfil"])
        print("Horário:", usuario["horario"])

        numero += 1



def consultar_usuario(usuarios):

    print("\n--- CONSULTAR USUÁRIO ---")

    usuario = escolher_usuario(usuarios)

    if usuario is None:
        return

    print("\nNome:", usuario["nome"])
    print("Matrícula:", mascarar_matricula(usuario["matricula"]))
    print("Perfil:", usuario["perfil"])
    print("Horário:", usuario["horario"])
    print("Observações:", usuario["observacoes"] or "-")



def revelar_matricula(usuarios):

    print("\n--- REVELAR MATRÍCULA ---")

    usuario = escolher_usuario(usuarios)

    if usuario is None:
        return

    print("\nMatrícula completa de", usuario["nome"] + ":", usuario["matricula"])

    registrar_auditoria("REVELAR_MATRICULA", usuario["matricula"], "matrícula exibida por completo")

    print("(Esta consulta foi registrada no log de auditoria.)")



def atualizar_usuario(usuarios):

    print("\n--- ATUALIZAR USUÁRIO ---")

    usuario = escolher_usuario(usuarios)

    if usuario is None:
        return

    print("Pressione ENTER para manter o dado atual.")

    alteracoes = []

    nome = input("Novo nome: ").strip()

    if nome:
        if not validar_nome(nome):
            print("Nome inválido.")
            return

        usuario["nome"] = nome
        alteracoes.append("nome")

    print("\n1 - Estudante")
    print("2 - Professor")
    print("3 - Administrador")

    opcao = input("Novo perfil: ")

    if opcao in PERFIS:
        usuario["perfil"] = PERFIS[opcao]
        alteracoes.append("perfil")

    elif opcao != "":
        print("Perfil inválido. Mantendo o anterior.")

    horario = input("Novo horário: ").strip()

    if horario:
        if validar_horario(horario):
            usuario["horario"] = horario
            alteracoes.append("horário")
        else:
            print("Horário inválido. Mantendo o anterior.")

    observacoes = input("Novas observações: ").strip()

    if observacoes:
        if ";" in observacoes:
            print("Observações inválidas.")
            return

        usuario["observacoes"] = observacoes
        alteracoes.append("observações")

    if len(alteracoes) == 0:
        print("Nada foi alterado.")
        return

    if salvar_usuarios(usuarios):
        registrar_auditoria("EDITAR_USUARIO", usuario["matricula"], "campos: " + ", ".join(alteracoes))
        print("Usuário atualizado com sucesso!")



def excluir_usuario(usuarios):

    print("\n--- EXCLUIR USUÁRIO ---")

    usuario = escolher_usuario(usuarios)

    if usuario is None:
        return

    print("Usuário:", usuario["nome"])

    confirmacao = input(
        "Deseja realmente excluir? (s/n): "
    ).lower()

    if confirmacao == "s":

        usuarios.remove(usuario)

        if salvar_usuarios(usuarios):
            registrar_auditoria("EXCLUIR_USUARIO", usuario["matricula"], usuario["nome"])
            print("Usuário excluído com sucesso! Os acessos dele continuam no histórico.")

    else:
        print("Exclusão cancelada.")


def menu_crud():

    usuarios = carregar_usuarios()

    while True:

        print("\n========== SENTINELALOG ==========")
        print("       GERENCIAMENTO DE USUÁRIOS")
        print("==================================")

        print("1 - Cadastrar usuário")
        print("2 - Listar usuários")
        print("3 - Consultar usuário")
        print("4 - Atualizar usuário")
        print("5 - Excluir usuário")
        print("6 - Revelar matrícula")
        print("0 - Voltar ao menu principal")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_usuario(usuarios)

        elif opcao == "2":
            listar_usuarios(usuarios)

        elif opcao == "3":
            consultar_usuario(usuarios)

        elif opcao == "4":
            atualizar_usuario(usuarios)

        elif opcao == "5":
            excluir_usuario(usuarios)

        elif opcao == "6":
            revelar_matricula(usuarios)

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")




if __name__ == "__main__":
    menu_crud()
