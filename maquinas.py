# ##########################################################################
# ##                                                                      ##
# ##   >>> NOVO EM 18/11 — Req. 3: Detecção de máquinas compartilhadas    ##
# ##                                                                      ##
# ##   O QUE FOI FEITO:                                                   ##
# ##   Opção 3 do menu principal. Agrupa os acessos por máquina e mostra  ##
# ##   um ALERTA para cada máquina usada por mais de um usuário,          ##
# ##   dizendo quem são (nome + matrícula mascarada) e quantas vezes      ##
# ##   cada um usou.                                                      ##
# ##                                                                      ##
# ##   POR QUÊ:                                                           ##
# ##   Se várias pessoas usam a mesma máquina, fica difícil saber quem    ##
# ##   fez uma ação a partir dela (ex.: quem apagou os arquivos).         ##
# ##   Só contamos acessos com SUCESSO: uma tentativa que falhou não      ##
# ##   chegou a usar a máquina, então não atrapalha a atribuição.         ##
# ##   As matrículas aparecem mascaradas, igual ao resto do sistema.      ##
# ##                                                                      ##
# ##########################################################################

from acessos import carregar_acessos
from auditoria import registrar_auditoria
from usuarios import carregar_usuarios, buscar_usuario, mascarar_matricula


def agrupar_usuarios_por_maquina(acessos):
    """Devolve {maquina: {matricula: quantidade_de_acessos_com_sucesso}}."""
    por_maquina = {}
    for acesso in acessos:
        if acesso["resultado"] != "sucesso":
            continue
        maquina = acesso["maquina"]
        matricula = acesso["matricula"]
        if maquina not in por_maquina:
            por_maquina[maquina] = {}
        por_maquina[maquina][matricula] = por_maquina[maquina].get(matricula, 0) + 1
    return por_maquina


def encontrar_maquinas_compartilhadas(acessos):
    """Só as máquinas usadas por 2 ou mais usuários diferentes, em ordem alfabética."""
    compartilhadas = {}
    por_maquina = agrupar_usuarios_por_maquina(acessos)
    for maquina in sorted(por_maquina):
        if len(por_maquina[maquina]) > 1:
            compartilhadas[maquina] = por_maquina[maquina]
    return compartilhadas


def nome_do_usuario(matricula, usuarios):
    usuario = buscar_usuario(matricula, usuarios)
    if usuario is None:
        return "(não cadastrado)"
    return usuario["nome"]


def mostrar_maquinas_compartilhadas():
    print(" MÁQUINAS COMPARTILHADAS \n")
    print("(Considera apenas acessos com sucesso.)\n")

    usuarios = carregar_usuarios()
    compartilhadas = encontrar_maquinas_compartilhadas(carregar_acessos())

    registrar_auditoria("CONSULTAR_MAQUINAS", "-",
                        f"{len(compartilhadas)} máquina(s) compartilhada(s)")

    if not compartilhadas:
        print("Nenhuma máquina foi usada por mais de um usuário.")
        return

    for maquina, contagem in compartilhadas.items():
        print("!" * 60)
        print(f"  ALERTA: {maquina} foi usada por {len(contagem)} usuários diferentes")
        print("!" * 60)
        for matricula, quantidade in contagem.items():
            print(f"  - {nome_do_usuario(matricula, usuarios):<30}"
                  f"{mascarar_matricula(matricula):<13}{quantidade} acesso(s)")
        print()

    print(f"Total: {len(compartilhadas)} máquina(s) compartilhada(s).")
    print("Ações feitas a partir delas não podem ser atribuídas a uma única pessoa.")
