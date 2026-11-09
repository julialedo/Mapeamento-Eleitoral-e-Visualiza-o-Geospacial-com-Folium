# Mapeamento Eleitoral e Visualização Geoespacial com Folium

Atividade prática da disciplina **Ferramentas para Data Science** (UFSJ / DCOMP), Prof.ª Carolina Xavier.

Análise e visualização da distribuição espacial dos votos da **eleição presidencial de 2026** (1º e 2º turnos)
por local de votação em **São João del-Rei (MG)**, usando `pandas`, `geopandas` e `folium`.

## Mapas

| Mapa | Arquivo | Situação |
|---|---|---|
| 1º turno: Flávio Bolsonaro (PL), mapa de calor | [`mapas/mapa_1turno_flavio.html`](mapas/mapa_1turno_flavio.html) | ✅ |
| 1º turno: Lula (PT), mapa de calor | [`mapas/mapa_1turno_lula.html`](mapas/mapa_1turno_lula.html) | ✅ |
| 1º turno: Augusto Cury (Avante), mapa de calor | [`mapas/mapa_1turno_cury.html`](mapas/mapa_1turno_cury.html) | ✅ |
| 1º turno: Renan Santos (Missão), mapa de calor | [`mapas/mapa_1turno_renan.html`](mapas/mapa_1turno_renan.html) | ✅ |
| 2º turno: Lula × Flávio Bolsonaro (paleta divergente) | [`mapas/mapa_2turno.html`](mapas/mapa_2turno.html) | ✅ |

Os mapas são arquivos HTML interativos: abra no navegador (é preciso internet para carregar o mapa de fundo).
Passe o mouse sobre os círculos (2º turno) ou sobre os pontos brancos (1º turno) para ver os detalhes de cada local
de votação.

## Estrutura do repositório

```
├── trabalho_sjdr.ipynb      # notebook: tratamento dos dados, mapas e relatório (Markdown)
├── recorte_sjdr.py          # gera os recortes de São João del-Rei a partir dos arquivos do TSE
├── dados_sjdr/
│   ├── votacao_presidente_sjdr.csv   # votos para presidente por seção (1º e 2º turnos)
│   └── locais_votacao_sjdr.csv       # locais de votação de cada seção, com latitude/longitude
├── mapas/                   # mapas interativos exportados (HTML)
└── environment.yml          # ambiente Conda com as versões exatas das bibliotecas
```

## Dados

Fonte: [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/).

| Arquivo original | Onde baixar | Uso |
|---|---|---|
| `votacao_secao_2026_BR.zip` | [Resultados 2026](https://dadosabertos.tse.jus.br/dataset/resultados-2026) → *Presidente - Votação por seção eleitoral - 2026* | votos por seção e candidato, nos dois turnos |
| `eleitorado_local_votacao_2026.zip` | [Eleitorado 2026](https://dadosabertos.tse.jus.br/dataset/eleitorado-2026) → *Eleitorado por local de votação - 2026* | endereço e coordenadas (latitude/longitude) de cada seção |

Os arquivos originais têm mais de 1 GB e passam do limite de tamanho do GitHub, por isso **não estão no repositório**.
A pasta `dados_sjdr/` contém o recorte de São João del-Rei (código do município no TSE: `52493`), gerado pelo
`recorte_sjdr.py`, sem nenhuma outra alteração nos dados.

## Como reproduzir

1. Crie o ambiente Conda:
   ```
   conda env create -f environment.yml
   conda activate folium_sjdr
   ```
2. Baixe os dois arquivos do TSE (links acima) e descompacte na pasta do projeto, mantendo os nomes das pastas
   (`votacao_secao_2026_BR/` e `eleitorado_local_votacao_2026/`).
3. Gere os recortes de São João del-Rei:
   ```
   python recorte_sjdr.py
   ```
4. Abra o `trabalho_sjdr.ipynb` com o kernel `folium_sjdr` e execute todas as células. Os mapas são salvos em `mapas/`.

O passo 2 e o 3 só são necessários para refazer os recortes: a pasta `dados_sjdr/` já está no repositório.

## Principais decisões de tratamento

As justificativas completas estão no notebook. Em resumo:

- **Chave de ligação** entre votos e locais: `NR_ZONA` + `NR_SECAO`.
- **Seções agregadas** foram descartadas: os eleitores delas votam na urna da seção principal, e os votos já estão
  contados nela.
- Os votos foram **somados por coordenada** (um círculo por prédio). Alguns prédios aparecem no TSE com códigos de local
  diferentes (por exemplo, o Colégio Tiradentes PMMG e o Campus Dom Bosco da UFSJ, que tem uma "Seção Especial" com
  código próprio).
- Os percentuais são calculados sobre os **votos válidos** (sem brancos e nulos).
- Nos **mapas de calor do 1º turno**, o peso de cada local é o número de **votos acima do esperado** pela média da
  cidade (votos válidos do local × % do candidato na cidade). Com os votos brutos, os quatro mapas mostrariam só onde
  há mais eleitores.

## Bibliotecas

`pandas`, `geopandas`, `folium` (e `branca`, que vem com o folium). As versões exatas estão no `environment.yml`.
