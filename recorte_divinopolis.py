from pathlib import Path

import pandas as pd

CD_MUNICIPIO = "44458"

PASTA = Path(__file__).parent
SAIDA = PASTA / "dados"

ARQUIVOS = [
    (
        PASTA / "eleitorado_local_votacao_2026" / "eleitorado_local_votacao_2026_MG.csv",
        "locais_votacao_divi.csv",
    ),
    (
        PASTA / "votacao_secao_2026_BR" / "votacao_secao_2026_BR.csv",
        "votacao_presidente_divi.csv",
    ),
]


def recortar(entrada: Path, saida: Path) -> None:
    if saida.exists():
        print(f"[já existe] {saida.relative_to(PASTA)} (apague o arquivo para gerar de novo)")
        return
    if not entrada.exists():
        print(f"[pulado] não encontrei {entrada.relative_to(PASTA)}")
        return

    print(f"Lendo {entrada.name} ...")
    pedacos = []
    for pedaco in pd.read_csv(
        entrada, sep=";", encoding="latin1", dtype=str, chunksize=500_000
    ):
        pedacos.append(pedaco[pedaco["CD_MUNICIPIO"] == CD_MUNICIPIO])

    df = pd.concat(pedacos, ignore_index=True)

    # Salva em UTF-8 para abrir sem problema de acento no notebook e no GitHub.
    df.to_csv(saida, sep=";", index=False, encoding="utf-8")
    print(f"  -> {len(df)} linhas salvas em {saida.relative_to(PASTA)}")
    print(f"  municípios no recorte: {df['NM_MUNICIPIO'].unique().tolist()}")
    print(f"  turnos no recorte: {sorted(df['NR_TURNO'].unique().tolist())}")


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    for entrada, nome_saida in ARQUIVOS:
        recortar(entrada, SAIDA / nome_saida)
