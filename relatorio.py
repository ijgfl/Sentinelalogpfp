# ##########################################################################
# ##                                                                      ##
# ##   >>> NOVO EM 18/11 — Req. 6: Relatório de segurança                 ##
# ##       (+ parte do Req. 7: gráfico por hora e exportação em .txt)     ##
# ##                                                                      ##
# ##   O QUE FOI FEITO:                                                   ##
# ##   Opção 5 do menu principal. Mostra o resumo do laboratório:         ##
# ##     - total de acessos e quantos falharam (com %)                    ##
# ##     - usuários que concentram mais falhas                            ##
# ##     - horários de mais movimento + gráfico de barras em texto        ##
# ##     - quantos acessos são normais, suspeitos e críticos              ##
# ##     - acessos vindos de máquinas bloqueadas e máquinas compartilhadas##
# ##   No fim, oferece exportar o relatório para dados/relatorio_*.txt.   ##
# ##                                                                      ##
# ##   POR QUÊ:                                                           ##
# ##   A Ana precisa de uma visão geral rápida, sem olhar acesso por      ##
# ##   acesso. O relatório é montado como uma LISTA DE LINHAS: a mesma    ##
# ##   lista serve para mostrar na tela e para gravar no arquivo, então   ##
# ##   não há código repetido. O arquivo exportado só tem matrículas      ##
# ##   mascaradas, porque ele pode ser enviado ou impresso.               ##
# ##                                                                      ##
# ##########################################################################

from datetime import datetime

from acessos import carregar_acessos
from arquivos import caminho
from auditoria import registrar_auditoria
from maquinas import encontrar_maquinas_compartilhadas
from risco import carregar_bloqueadas
from usuarios import carregar_usuarios, buscar_usuario, mascarar_matricula
from utils import converter_data_hora, formatar_data_hora, ler_sim_nao

QUANTIDADE_RANKING = 5
LARGURA_MAXIMA_BARRA = 40


def porcentagem(parte, total):
    if total == 0:
        return 0.0
    return parte * 100 / total


def contar_falhas_por_matricula(acessos):
    falhas = {}
    for acesso in acessos:
        if acesso["resultado"] == "falha":
            falhas[acesso["matricula"]] = falhas.get(acesso["matricula"], 0) + 1
    return falhas


def contar_acessos_por_hora(acessos):
    """Devolve uma lista com 24 posições: quantidade de acessos em cada hora do dia."""
    por_hora = [0] * 24
    for acesso in acessos:
        momento = converter_data_hora(acesso["data_hora"])
        if momento is not None:
            por_hora[momento.hour] += 1
    return por_hora


def contar_classificacoes(acessos):
    contagem = {"normal": 0, "suspeito": 0, "crítico": 0}
    for acesso in acessos:
        if acesso["classificacao"] in contagem:
            contagem[acesso["classificacao"]] += 1
    return contagem


def ordenar_por_quantidade(dicionario):
    """Ordena os pares (chave, quantidade) da maior quantidade para a menor."""
    return sorted(dicionario.items(), key=lambda par: par[1], reverse=True)


def linhas_ranking_falhas(acessos, usuarios):
    linhas = ["USUÁRIOS COM MAIS FALHAS"]
    ranking = ordenar_por_quantidade(contar_falhas_por_matricula(acessos))
    if not ranking:
        linhas.append("  Nenhuma falha registrada.")
    for posicao, (matricula, quantidade) in enumerate(ranking[:QUANTIDADE_RANKING], start=1):
        usuario = buscar_usuario(matricula, usuarios)
        nome = usuario["nome"] if usuario else "(não cadastrado)"
        linhas.append(f"  {posicao}. {nome:<28}{mascarar_matricula(matricula):<13}"
                      f"{quantidade} falha(s)")
    return linhas


def linhas_movimento_por_hora(acessos):
    por_hora = contar_acessos_por_hora(acessos)
    maior = max(por_hora)
    linhas = ["HORÁRIOS DE MAIS MOVIMENTO"]
    if maior == 0:
        linhas.append("  Sem dados.")
        return linhas

    horas_ordenadas = sorted(range(24), key=lambda hora: por_hora[hora], reverse=True)
    for hora in horas_ordenadas[:3]:
        if por_hora[hora] > 0:
            linhas.append(f"  {hora:02d}h: {por_hora[hora]} acesso(s)")

    # Gráfico de barras em texto (Req. 7): uma linha por hora que teve acesso
    linhas.append("")
    linhas.append("  Movimento por hora (* = fora do funcionamento 7h-22h)")
    for hora in range(24):
        if por_hora[hora] == 0:
            continue
        tamanho = max(1, round(por_hora[hora] * LARGURA_MAXIMA_BARRA / maior))
        marcador = "*" if hora < 7 or hora >= 22 else " "
        linhas.append(f"  {hora:02d}h{marcador} {'█' * tamanho} {por_hora[hora]}")
    return linhas


def montar_relatorio():
    acessos = carregar_acessos()
    usuarios = carregar_usuarios()
    total = len(acessos)
    falhas = sum(1 for acesso in acessos if acesso["resultado"] == "falha")
    classificacoes = contar_classificacoes(acessos)
    bloqueadas = carregar_bloqueadas()
    vindos_de_bloqueadas = sum(1 for acesso in acessos if acesso["maquina"] in bloqueadas)
    compartilhadas = encontrar_maquinas_compartilhadas(acessos)

    linhas = [
        "RELATÓRIO DE SEGURANÇA — SENTINELALOG",
        f"Gerado em {formatar_data_hora(datetime.now())}",
        "=" * 60,
        "",
        "VISÃO GERAL",
        f"  Acessos registrados: {total}",
        f"  Acessos com falha:   {falhas} ({porcentagem(falhas, total):.1f}%)",
        f"  Usuários cadastrados: {len(usuarios)}",
        "",
        "CLASSIFICAÇÃO DE RISCO",
    ]
    for nome, quantidade in classificacoes.items():
        linhas.append(f"  {nome.capitalize():<10}{quantidade:>5} ({porcentagem(quantidade, total):.1f}%)")
    linhas.append(f"  Suspeitos + críticos: {classificacoes['suspeito'] + classificacoes['crítico']}")
    linhas.append("")
    linhas.extend(linhas_ranking_falhas(acessos, usuarios))
    linhas.append("")
    linhas.extend(linhas_movimento_por_hora(acessos))
    linhas.append("")
    linhas.append("OUTROS ALERTAS")
    linhas.append(f"  Acessos vindos de máquinas bloqueadas: {vindos_de_bloqueadas}")
    linhas.append(f"  Máquinas usadas por mais de um usuário: {len(compartilhadas)}"
                  + (f" ({', '.join(compartilhadas)})" if compartilhadas else ""))
    return linhas


def exportar_relatorio(linhas):
    nome_arquivo = "relatorio_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
    try:
        with open(caminho(nome_arquivo), "w", encoding="utf-8") as arquivo:
            arquivo.write("\n".join(linhas) + "\n")
    except OSError as erro:
        print(f"Erro ao exportar o relatório: {erro}")
        return
    registrar_auditoria("EXPORTAR_RELATORIO", "-", nome_arquivo)
    print(f"Relatório salvo em dados/{nome_arquivo}")


def mostrar_relatorio():
    linhas = montar_relatorio()
    for linha in linhas:
        print(linha)
    registrar_auditoria("GERAR_RELATORIO", "-", "relatório de segurança exibido")
    print()
    if ler_sim_nao("Exportar este relatório para um arquivo .txt? (s/n): "):
        exportar_relatorio(linhas)
