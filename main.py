from acessos import menu_acessos, ARQUIVO_ACESSOS, CAMPOS_ACESSO
from arquivos import garantir_arquivo
from assistente_ia import menu_assistente_ia
from auditoria import ARQUIVO_AUDITORIA, CAMPOS_AUDITORIA
from risco import ARQUIVO_BLOQUEADAS
from usuarios import menu_crud, ARQUIVO_USUARIOS, CAMPOS_USUARIO
from utils import limpar_tela, pausar, ler_opcao


def preparar_arquivos():
    garantir_arquivo(ARQUIVO_USUARIOS, CAMPOS_USUARIO)
    garantir_arquivo(ARQUIVO_ACESSOS, CAMPOS_ACESSO)
    garantir_arquivo(ARQUIVO_AUDITORIA, CAMPOS_AUDITORIA)
    garantir_arquivo(ARQUIVO_BLOQUEADAS)


def em_breve(funcionalidade):
    print(f"\n{funcionalidade}: ainda em desenvolvimento.")
    pausar()


def mostrar_menu():
    limpar_tela()
    print("   SENTINELALOG — Monitor de Acessos do Laboratório")
    print("=" * 52)
    print("1. Usuários")
    print("2. Acessos")
    print("3. Máquinas compartilhadas   (em breve)")
    print("4. Log de auditoria          (em breve)")
    print("5. Relatório de segurança    (em breve)")
    print("6. Funcionalidade extra      (em breve)")
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
            em_breve("Detecção de máquinas compartilhadas")
        elif opcao == "4":
            em_breve("Consulta do log de auditoria")
        elif opcao == "5":
            em_breve("Relatório de segurança")
        elif opcao == "6":
            em_breve("Funcionalidade extra")
        elif opcao == "7":
            menu_assistente_ia()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        #Ctrl+C ou fim da entrada encerra sem mostrar erro na tela
        print("\n\nPrograma encerrado.")
