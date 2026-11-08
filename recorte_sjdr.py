"""
Recorta os arquivos do TSE para ficar só com São João del-Rei.

Por que existe este script:
    Os CSVs do TSE vêm com o estado (ou o Brasil) inteiro e alguns passam de 1 GB.
    Abrir isso no notebook toda vez é lento e trava a memória. Então lemos o
    arquivo em pedaços (chunks), guardamos só as linhas de São João del-Rei e
    salvamos um CSV pequeno em dados_sjdr/. O notebook usa só esses recortes.

Como rodar (no terminal, dentro da pasta atividade_folium):
    python recorte_sjdr.py
"""

from pathlib import Path

import pandas as pd

# Código do município no TSE (não é o código do IBGE!).
# São João del-Rei = 52493. Conferido no arquivo votacao_secao_2026_MG.csv.
CD_MUNICIPIO_SJDR = "52493"

PASTA = Path(__file__).parent
SAIDA = PASTA / "dados_sjdr"

# (arquivo de entrada, nome do arquivo de saída)
# Se um arquivo ainda não foi baixado, o script avisa e pula.
ARQUIVOS = [
    (
        PASTA / "eleitorado_local_votacao_2026" / "eleitorado_local_votacao_2026_MG.csv",
        "locais_votacao_sjdr.csv",
    ),
    # Arquivo "Presidente - Votação por seção eleitoral - 2026" (Brasil inteiro).
    (
        PASTA / "votacao_secao_2026_BR" / "votacao_secao_2026_BR.csv",
        "votacao_presidente_sjdr.csv",
    ),
]


def recortar(entrada: Path, saida: Path) -> None:
    if not entrada.exists():
        print(f"[pulado] não encontrei {entrada.relative_to(PASTA)}")
        return

    print(f"Lendo {entrada.name} ...")
    pedacos = []
    # sep=";"            -> o TSE separa colunas com ponto e vírgula
    # encoding="latin1"  -> os arquivos do TSE não são UTF-8 (acentos viram lixo sem isso)
    # dtype=str          -> lê tudo como texto; assim "52493" e "-21,68" não são
    #                       convertidos errado. Convertemos os números no notebook.
    # chunksize          -> lê 500 mil linhas por vez em vez do arquivo todo
    for pedaco in pd.read_csv(
        entrada, sep=";", encoding="latin1", dtype=str, chunksize=500_000
    ):
        pedacos.append(pedaco[pedaco["CD_MUNICIPIO"] == CD_MUNICIPIO_SJDR])

    df = pd.concat(pedacos, ignore_index=True)

    # Salva em UTF-8 para abrir sem problema de acento no notebook e no GitHub.
    df.to_csv(saida, sep=";", index=False, encoding="utf-8")
    print(f"  -> {len(df)} linhas salvas em {saida.relative_to(PASTA)}")
    print(f"  municípios no recorte: {df['NM_MUNICIPIO'].unique().tolist()}")
    # Conferência: quais turnos vieram no arquivo? Esperamos ['1', '2'].
    print(f"  turnos no recorte: {sorted(df['NR_TURNO'].unique().tolist())}")


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    for entrada, nome_saida in ARQUIVOS:
        recortar(entrada, SAIDA / nome_saida)
