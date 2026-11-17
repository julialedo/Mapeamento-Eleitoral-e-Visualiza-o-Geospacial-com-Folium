import json
from pathlib import Path

import pandas as pd
import streamlit as st

PASTA = Path(__file__).parent
MAPAS = PASTA / "mapas"
RESULTADOS = PASTA / "resultados"
NOTEBOOK = PASTA / "trabalho_divinopolis.ipynb"

# Os 4 principais candidatos do 1º turno: nome do arquivo do mapa e partido
CANDIDATOS_1T = {
    "Flávio Bolsonaro": ("flavio", "PL"),
    "Lula": ("lula", "PT"),
    "Augusto Cury": ("cury", "Avante"),
    "Renan Santos": ("renan", "Missão"),
}
ALTURA_MAPA = 600              
MIN_VALIDOS_BAIRRO = 1500      


def pct_br(valor):
    """53.98 -> '54,0%'"""
    return f"{valor:.1f}%".replace(".", ",")


def num_br(valor):
    """71478 -> '71.478'"""
    return f"{int(round(valor)):,}".replace(",", ".")


def saldo_br(valor):
    """1411.3 -> '+1.411'; -321 -> '-321'"""
    sinal = "+" if valor >= 0 else "-"
    return sinal + num_br(abs(valor))


ARQUIVOS_NECESSARIOS = (
    [RESULTADOS / nome for nome in ("ranking_1turno.csv", "locais_1turno.csv", "locais_2turno.csv")]
    + [MAPAS / f"mapa_1turno_{arquivo}.html" for arquivo, _ in CANDIDATOS_1T.values()]
    + [MAPAS / "mapa_2turno.html"]
)


@st.cache_data
def carregar_tabelas():
    """Ranking do 1º turno e um resumo de cada local de votação nos dois turnos."""
    def ler(nome):
        return pd.read_csv(RESULTADOS / nome, sep=";", dtype={"NR_ZONA": str, "SECOES": str})

    return ler("ranking_1turno.csv"), ler("locais_1turno.csv"), ler("locais_2turno.csv")


def mostrar_mapa(nome_arquivo):
    st.iframe(MAPAS / nome_arquivo, height=ALTURA_MAPA)


@st.cache_data
def ler_observacoes(modificado_em):
    observacoes = {}
    for celula in json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]:
        texto = "".join(celula["source"])
        if celula["cell_type"] == "markdown" and texto.startswith("#### Relatório – Mapa do ") and "**O fato**" in texto:
            mapa = texto.splitlines()[0].removeprefix("#### Relatório – Mapa do ").strip()
            observacoes[mapa] = texto.split("**O fato**", 1)[1].split("**O design**", 1)[0].strip()
    return observacoes


def mostrar_observacoes(mapa):
    st.markdown("#### Observações")
    texto = ler_observacoes(NOTEBOOK.stat().st_mtime).get(mapa) if NOTEBOOK.exists() else None
    st.markdown(texto or "_Não encontrei as observações deste mapa no trabalho_divinopolis.ipynb._")


def regioes(locais):
    """Grupos de locais para comparar: cada zona eleitoral, a sede e a zona rural."""
    grupos = {f"Zona {zona}": tabela for zona, tabela in locais.groupby("NR_ZONA")}
    grupos["Sede"] = locais[~locais["FORA_DA_SEDE"]]
    grupos["Zona rural"] = locais[locais["FORA_DA_SEDE"]]
    return grupos


def analises_1turno(candidato, ranking, locais):
    linha = ranking.loc[ranking["NOME"] == candidato].iloc[0]
    pct_cidade = linha["PCT_DIVI"]

    st.markdown("#### Resultado na cidade")
    col = st.columns(4)
    col[0].metric("Votos", num_br(linha["QT_VOTOS"]))
    col[1].metric("% dos votos válidos", pct_br(pct_cidade))
    col[2].metric("Posição", f"{int(linha['POS_DIVI'])}º de {len(ranking)}")
    col[3].metric("Locais em que liderou", f"{(locais['LIDER'] == candidato).sum()} de {len(locais)}")

    st.markdown("#### Por região")
    grupos = regioes(locais)
    for coluna, (nome, tabela) in zip(st.columns(len(grupos)), grupos.items()):
        pct = 100 * tabela[f"VOTOS_{candidato}"].sum() / tabela["VALIDOS"].sum()
        coluna.metric(nome, pct_br(pct))

    st.markdown("#### Onde ficou acima e abaixo da média")
    saldo = locais.groupby("NM_BAIRRO")[f"ACIMA_{candidato}"].sum()
    esquerda, direita = st.columns(2)
    for coluna, titulo, bairros in (
        (esquerda, "Bairros mais acima da média", saldo.nlargest(5)),
        (direita, "Bairros mais abaixo da média", saldo.nsmallest(5)),
    ):
        coluna.markdown(f"**{titulo}**")
        coluna.dataframe(
            pd.DataFrame({"Bairro": bairros.index, "Saldo (votos)": bairros.map(saldo_br).values}),
            hide_index=True,
            width="stretch",
        )

    st.markdown("**Locais de votação com maior saldo**")
    melhores = locais.nlargest(5, f"ACIMA_{candidato}")
    st.dataframe(
        pd.DataFrame({
            "Local de votação": melhores["NM_LOCAL_VOTACAO"],
            "Bairro": melhores["NM_BAIRRO"],
            "Zona": melhores["NR_ZONA"],
            "% no local": melhores[f"PCT_{candidato}"].map(pct_br),
            "Saldo (votos)": melhores[f"ACIMA_{candidato}"].map(saldo_br),
        }),
        hide_index=True,
        width="stretch",
    )


def analises_2turno(locais):
    flavio, lula = locais["FLAVIO"].sum(), locais["LULA"].sum()
    validos, total = flavio + lula, locais["TOTAL"].sum()
    pct_lula_cidade = 100 * lula / validos

    st.markdown("#### Resultado na cidade")
    col = st.columns(4)
    col[0].metric("Flávio Bolsonaro (PL)", pct_br(100 * flavio / validos))
    col[1].metric("Lula (PT)", pct_br(pct_lula_cidade))
    col[2].metric("Diferença", f"{num_br(abs(flavio - lula))} votos")
    col[3].metric("Brancos e nulos", pct_br(100 * (total - validos) / total))
    st.caption(f"Flávio: {num_br(flavio)} votos · Lula: {num_br(lula)} votos · total de votos: {num_br(total)}")

    vencedores = locais["VENCEDOR"].value_counts()
    col = st.columns(3)
    col[0].metric("Locais em que o Flávio venceu", f"{vencedores.get('Flávio Bolsonaro', 0)} de {len(locais)}")
    col[1].metric("Locais em que o Lula venceu", f"{vencedores.get('Lula', 0)} de {len(locais)}")
    col[2].metric("Empates", int(vencedores.get("Empate", 0)))

    st.markdown("#### % do Lula por região")
    grupos = regioes(locais)
    for coluna, (nome, tabela) in zip(st.columns(len(grupos)), grupos.items()):
        pct = 100 * tabela["LULA"].sum() / tabela["VALIDOS"].sum()
        coluna.metric(nome, pct_br(pct))

    st.markdown("#### Bairros onde cada um foi mais forte")
    st.caption(f"Só bairros com pelo menos {num_br(MIN_VALIDOS_BAIRRO)} votos válidos.")
    bairros = locais.groupby("NM_BAIRRO")[["FLAVIO", "LULA", "VALIDOS"]].sum()
    bairros = bairros[bairros["VALIDOS"] >= MIN_VALIDOS_BAIRRO]
    bairros["PCT_FLAVIO"] = 100 * bairros["FLAVIO"] / bairros["VALIDOS"]
    bairros["PCT_LULA"] = 100 * bairros["LULA"] / bairros["VALIDOS"]
    esquerda, direita = st.columns(2)
    for coluna, titulo, nome, campo in (
        (esquerda, "Mais votados no Flávio", "Flávio", "PCT_FLAVIO"),
        (direita, "Mais votados no Lula", "Lula", "PCT_LULA"),
    ):
        melhores = bairros.nlargest(5, campo)
        coluna.markdown(f"**{titulo}**")
        coluna.dataframe(
            pd.DataFrame({
                "Bairro": melhores.index,
                "Votos válidos": melhores["VALIDOS"].map(num_br).values,
                f"% do {nome}": melhores[campo].map(pct_br).values,
            }),
            hide_index=True,
            width="stretch",
        )


st.set_page_config(page_title="Eleição 2026 em Divinópolis", layout="wide")
st.title("Eleição presidencial 2026 em Divinópolis (MG)")

faltando = [str(arquivo.relative_to(PASTA)) for arquivo in ARQUIVOS_NECESSARIOS if not arquivo.exists()]
if faltando:
    st.error(
        "Faltam arquivos gerados pelo notebook: " + ", ".join(faltando) + ". "
        "Rode o trabalho_divinopolis.ipynb do começo ao fim e recarregue esta página."
    )
    st.stop()

ranking, locais_1t, locais_2t = carregar_tabelas()

with st.sidebar:
    st.header("Escolha o mapa")
    turno = st.radio("Turno", ["1º turno", "2º turno"])
    if turno == "1º turno":
        candidato = st.selectbox("Candidato", list(CANDIDATOS_1T))
    else:
        st.caption("No 2º turno, um único mapa compara os dois finalistas.")

if turno == "1º turno":
    arquivo, partido = CANDIDATOS_1T[candidato]
    st.subheader(f"1º turno – {candidato} ({partido})")
    mostrar_mapa(f"mapa_1turno_{arquivo}.html")
    mostrar_observacoes(f"1º turno: {candidato}")
    analises_1turno(candidato, ranking, locais_1t)
else:
    st.subheader("2º turno – Flávio Bolsonaro (PL) × Lula (PT)")
    mostrar_mapa("mapa_2turno.html")
    mostrar_observacoes("2º turno")
    analises_2turno(locais_2t)
