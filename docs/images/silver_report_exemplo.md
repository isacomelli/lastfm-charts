# Silver Layer - Relatório de Qualidade de Dados

**Data de geração:** 2026-03-29 14:04

**Total de registros:** 1,508,168

**Período coberto:** 2010-07-06 18:22:52+00:00 → 2026-03-29 16:38:39+00:00

## Tipos de Colunas

| Coluna | Tipo |
|---|---|
| image | str |
| track_name | str |
| username | str |
| artist_name | str |
| album_name | str |
| timestamp_unix | int64 |
| datetime_raw | str |
| datetime_utc | datetime64[s, UTC] |
| year | int32 |
| month | int32 |
| month_name | str |
| day | int32 |
| hour | int32 |
| weekday | int32 |
| weekday_name | str |
| week_of_year | int64 |
| quarter | int32 |
| semester | int64 |
| title | str |
| year_month | period[M] |

## Valores Nulos

| Coluna | Nulos |
|---|---|
| album_name | 12,250 (0.8%) |

## Estatísticas Descritivas

|       |         hour |     weekday |        month |           year |
|:------|-------------:|------------:|-------------:|---------------:|
| count |  1.50817e+06 | 1.50817e+06 |  1.50817e+06 |    1.50817e+06 |
| mean  | 13.6925      | 2.85084     |  6.56938     | 2021.42        |
| std   |  6.935       | 1.958       |  3.44336     |    3.58442     |
| min   |  0           | 0           |  1           | 2010           |
| 25%   | 10           | 1           |  4           | 2020           |
| 50%   | 15           | 3           |  7           | 2022           |
| 75%   | 19           | 4           | 10           | 2024           |
| max   | 23           | 6           | 12           | 2026           |

## Gráficos

![g1_scrobbles_por_usuario.png](graphs/g1_scrobbles_por_usuario_exemplo.png)

![g2_top10_artistas.png](graphs/g2_top10_artistas_exemplo.png)

![g3_hora_do_dia.png](graphs/g3_hora_do_dia_exemplo.png)

![g4_dia_da_semana.png](graphs/g4_dia_da_semana_exemplo.png)

![g5_evolucao_mensal.png](graphs/g5_evolucao_mensal_exemplo.png)

![g6_outliers_por_usuario.png](graphs/g6_outliers_por_usuario_exemplo.png)