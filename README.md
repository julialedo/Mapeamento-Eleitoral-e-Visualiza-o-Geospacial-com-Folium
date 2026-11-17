# Mapeamento Eleitoral e Visualização Geoespacial com Folium

Atividade prática da disciplina Ferramentas para Data Science.

Análise e visualização da distribuição espacial dos votos da eleição presidencial de 2026 (1º e 2º turnos)
por local de votação em Divinópolis (MG).

## Mapas

| Mapa                                                     | Arquivo                                                           |
| -------------------------------------------------------- | ----------------------------------------------------------------- |
| 1º turno: Flávio Bolsonaro (PL), mapa de calor         | [`mapas/mapa_1turno_flavio.html`](mapas/mapa_1turno_flavio.html) |
| 1º turno: Lula (PT), mapa de calor                      | [`mapas/mapa_1turno_lula.html`](mapas/mapa_1turno_lula.html)     |
| 1º turno: Augusto Cury (Avante), mapa de calor          | [`mapas/mapa_1turno_cury.html`](mapas/mapa_1turno_cury.html)     |
| 1º turno: Renan Santos (Missão), mapa de calor         | [`mapas/mapa_1turno_renan.html`](mapas/mapa_1turno_renan.html)   |
| 2º turno: Lula × Flávio Bolsonaro (paleta divergente) | [`mapas/mapa_2turno.html`](mapas/mapa_2turno.html)               |

## Estrutura do repositório

```
├── trabalho_divinopolis.ipynb      # notebook: tratamento dos dados, mapas e relatório (Markdown)
├── recorte_divinopolis.py          # gera os recortes de Divinópolis a partir dos arquivos do TSE
├── dados/
│   ├── votacao_presidente_divi.csv   # votos para presidente por seção (1º e 2º turnos)
│   └── locais_votacao_divi.csv       # locais de votação de cada seção, com latitude/longitude
├── mapas/                   # mapas interativos exportados (HTML)
└── environment.yml          # ambiente Conda com as versões exatas das bibliotecas
```

## Dados

Fonte: [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/).

| Arquivo original                      | Onde baixar                                                                                                                          | Uso                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| `votacao_secao_2026_BR.zip`         | [Resultados 2026](https://dadosabertos.tse.jus.br/dataset/resultados-2026) → *Presidente - Votação por seção eleitoral - 2026* | votos por seção e candidato, nos dois turnos               |
| `eleitorado_local_votacao_2026.zip` | [Eleitorado 2026](https://dadosabertos.tse.jus.br/dataset/eleitorado-2026) → *Eleitorado por local de votação - 2026*            | endereço e coordenadas (latitude/longitude) de cada seção |

Os arquivos originais têm mais de 1 GB e passam do limite de tamanho do GitHub, por isso não estão no repositório.
A pasta `dados/` contém o recorte de Divinópolis (código do município no TSE: `44458`), gerado pelo
`recorte_divinopolis.py`, sem nenhuma outra alteração nos dados.

## Como reproduzir

1. Crie o ambiente Conda:
   ```
   conda env create -f environment.yml
   conda activate folium_divinopolis
   ```
2. Baixe os dois arquivos do TSE (links acima) e descompacte na pasta do projeto, mantendo os nomes das pastas
   (`votacao_secao_2026_BR/` e `eleitorado_local_votacao_2026/`).
3. Gere os recortes de Divinópolis:
   ```
   python recorte_divinopolis.py
   ```
4. Abra o `trabalho_divinopolis.ipynb` com o kernel `folium_divinopolis` e execute todas as células. Os mapas são salvos em `mapas/`.

O passo 2 e o 3 só são necessários para refazer os recortes: a pasta `dados/` já está no repositório.

## Dashboard

O `dashboard_divinopolis.py` (Streamlit) reúne os 5 mapas: escolha o turno e, no 1º turno, o candidato.
Abaixo de cada mapa aparecem as observações do relatório e algumas análises simples.

Depois de rodar o notebook (ele gera as pastas `mapas/` e `resultados/`), abra o dashboard com:
```
streamlit run dashboard_divinopolis.py
```

## Principais decisões de tratamento

- Chave de ligação entre votos e locais: `NR_ZONA` + `NR_SECAO`.
- Seções agregadas foram descartadas: os eleitores delas votam na urna da seção principal, e os votos já estão
  contados nela.
- Os votos foram somados por coordenada (um círculo por prédio).
- Os percentuais são calculados sobre os votos válidos (sem brancos e nulos).
- Nos mapas de calor do 1º turno, o peso de cada local é o número de votos acima do esperado pela média da
  cidade (votos válidos do local × % do candidato na cidade).
