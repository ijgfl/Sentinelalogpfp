from acessos import menu_acessos, ARQUIVO_ACESSOS, CAMPOS_ACESSO
from arquivos import garantir_arquivo
from assistente_ia import menu_assistente_ia
from auditoria import ARQUIVO_AUDITORIA, CAMPOS_AUDITORIA
from risco import ARQUIVO_BLOQUEADAS
from usuarios import menu_crud, ARQUIVO_USUARIOS, CAMPOS_USUARIO
from utils import limpar_tela, pausar, ler_opcao

# ##########################################################################
# ##   >>> NOVO EM 18/11 — imports das opções 3, 4, 5 e 6 do menu         ##
# ##   Cada requisito novo ficou no próprio arquivo, para o código não    ##
# ##   virar um arquivo gigante e cada pessoa do grupo conseguir          ##
# ##   explicar a sua parte separadamente na apresentação.               ##
# ##########################################################################
from consulta_auditoria import menu_auditoria      # Req. 4
from maquinas import mostrar_maquinas_compartilhadas  # Req. 3
from relatorio import mostrar_relatorio            # Req. 6 (+ exportação)
from simulacao import menu_simulacao               # Req. 7


def preparar_arquivos():
    garantir_arquivo(ARQUIVO_USUARIOS, CAMPOS_USUARIO)
    garantir_arquivo(ARQUIVO_ACESSOS, CAMPOS_ACESSO)
    garantir_arquivo(ARQUIVO_AUDITORIA, CAMPOS_AUDITORIA)
    garantir_arquivo(ARQUIVO_BLOQUEADAS)


# ##########################################################################
# ##   >>> ALTERADO EM 18/11 — a função em_breve() foi substituída        ##
# ##   O QUE FOI FEITO: as opções 3 a 6 deixaram de mostrar "em breve"    ##
# ##   e agora chamam as funções novas.                                   ##
# ##   POR QUÊ: executar_tela() limpa a tela, roda a função e pausa;      ##
# ##   assim esse padrão não se repete em cada "elif".                    ##
# ##########################################################################
def executar_tela(funcao):
    limpar_tela()
    funcao()
    pausar()


def mostrar_menu():
    limpar_tela()
    print("   SENTINELALOG — Monitor de Acessos do Laboratório")
    print("=" * 52)
    print("1. Usuários")
    print("2. Acessos")
    print("3. Máquinas compartilhadas")
    print("4. Log de auditoria")
    print("5. Relatório de segurança")
    print("6. Simulação de acessos (extra)")
    print("7. Assistente de IA")
    print("0. Sair")


def main():
    preparar_arquivos()
    while True:
        mostrar_menu()
        opcao = ler_opcao("\nEscolha uma opção: ", ["0", "1", "2", "3", "4", "5", "6", "7"])
        if opcao == "0":
            print("\nAté logo!")
            break
        elif opcao == "1":
            menu_crud()
        elif opcao == "2":
            menu_acessos()
        elif opcao == "3":
            executar_tela(mostrar_maquinas_compartilhadas)   # NOVO — Req. 3
        elif opcao == "4":
            menu_auditoria()                                 # NOVO — Req. 4
        elif opcao == "5":
            executar_tela(mostrar_relatorio)                 # NOVO — Req. 6
        elif opcao == "6":
            executar_tela(menu_simulacao)                    # NOVO — Req. 7
        elif opcao == "7":
            menu_assistente_ia()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        #Ctrl+C ou fim da entrada encerra sem mostrar erro na tela
        print("\n\nPrograma encerrado.")
