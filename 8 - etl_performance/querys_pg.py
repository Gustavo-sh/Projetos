VIEW_AEC = f"""
SELECT
    data,
    chave_externa,
    COALESCE(chave_externa_supervisor, 0) AS chave_externa_supervisor,
    COALESCE(chave_externa_coordenador, 0) AS chave_externa_coordenador,
    COALESCE(chave_externa_superintendente, 0) AS chave_externa_gerente_executivo,
    COALESCE(chave_externa_diretor_de_atendimento, 0) AS chave_externa_diretor_de_atendimento,
    --COALESCE(chave_externa_diretor_atendimento, 0) AS chave_externa_diretor_de_atendimento,
    COALESCE(chave_externa_diretor, 0) AS chave_externa_diretor,
    UPPER(segmento) as segmento,
    id_indicador,
    nome_indicador,
    resultado,
    fator,
    resultado_calculado,
    percentual_atingimento,
    meta,
    ganho,
    max_ganho,
    id_grupo,
    COALESCE(chave_externa_gerente_jr, 0) AS chave_externa_gerente_jr,
    COALESCE(chave_externa_gerente_pl, 0) AS chave_externa_gerente_pl,
    COALESCE(chave_externa_gerente_sr, 0) AS chave_externa_gerente_sr,
    fator_2,
    fator_3,
    fator_4
FROM public.performance_view
--FROM "views".performance_view
WHERE data=%s
and id_indicador <> 86
and nome_nivel_hierarquia = '1'
and segmento not ilike %s
"""

VIEW_SANTANDER = f"""
SELECT
    data,
    chave_externa::int,
    COALESCE(REPLACE(chave_externa_supervisor, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_supervisor,
    COALESCE(REPLACE(chave_externa_coordenador, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_coordenador,
    COALESCE(REPLACE(chave_externa_superintendente, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_gerente_executivo,
    COALESCE(REPLACE(chave_externa_diretor_de_atendimento, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_diretor_de_atendimento,
    COALESCE(REPLACE(chave_externa_diretor, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_diretor,
    UPPER(segmento) as segmento,
    (CASE WHEN id_indicador = -5 THEN 34 WHEN id_indicador = -1 THEN 86 ELSE id_indicador END)::int as id_indicador,
    nome_indicador,
    REPLACE(resultado, ',', '.')::float as resultado,
    REPLACE(fator, ',', '.')::float as fator,
    REPLACE(resultado_calculado, ',', '.')::float as resultado_calculado,
    REPLACE(percentual_atingimento, ',', '.')::float as percentual_atingimento,
    REPLACE(meta, ',', '.')::float as meta,
    ganho::int,
    max_ganho::int,
    id_grupo::int,
    COALESCE(REPLACE(chave_externa_gerente_jr, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_gerente_jr,
    COALESCE(REPLACE(chave_externa_gerente_pl, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_gerente_pl,
    COALESCE(REPLACE(chave_externa_gerente_sr, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_gerente_sr,
    REPLACE(fator_2, ',', '.')::float as fator_2,
    REPLACE(fator_3, ',', '.')::float as fator_3,
    REPLACE(fator_4, ',', '.')::float as fator_4
FROM public.performance
WHERE data=%s
and id_indicador <> -1
and nome_nivel_hierarquia = 'OPERACIONAL'
and segmento ilike %s
"""

TABELA_AEC = f"""
SELECT
    data,
    CAST(chave_externa AS int) AS chave_externa,
    CAST(
        CASE
            WHEN nome_nivel_hierarquia = 'operacional' THEN 1
            WHEN nome_nivel_hierarquia = 'supervisor' THEN 2
            WHEN nome_nivel_hierarquia = 'coordenador' THEN 3
            WHEN nome_nivel_hierarquia = 'gerente' THEN 4
            WHEN nome_nivel_hierarquia = 'gerente jr' THEN 5
            WHEN nome_nivel_hierarquia = 'gerente pl' THEN 6
            WHEN nome_nivel_hierarquia = 'gerente sr' THEN 7
            WHEN nome_nivel_hierarquia = 'superintendente' THEN 8
            WHEN nome_nivel_hierarquia = 'diretor de atendimento' THEN 9
            WHEN nome_nivel_hierarquia = 'diretor' THEN 10
            WHEN nome_nivel_hierarquia = 'presidente' THEN 11
            WHEN nome_nivel_hierarquia = 'conselheiro' THEN 12
            WHEN nome_nivel_hierarquia = 'superintendente' THEN 13
            WHEN nome_nivel_hierarquia = 'sem informação' THEN 0
            ELSE 50
        END AS int
    ) AS nome_nivel_hierarquia,
    CASE
        WHEN trim(chave_externa_supervisor) ~ '^[0-9]+$'
            THEN trim(chave_externa_supervisor)::int
        ELSE 0
    END AS chave_externa_supervisor,
    CASE
        WHEN trim(chave_externa_coordenador) ~ '^[0-9]+$'
            THEN trim(chave_externa_coordenador)::int
        ELSE 0
    END AS chave_externa_coordenador,
    CASE
        WHEN trim(chave_externa_superintendente) ~ '^[0-9]+$'
            THEN trim(chave_externa_superintendente)::int
        ELSE 0
    END AS chave_externa_gerente_executivo,
    CASE
        WHEN trim(chave_externa_diretor_de_atendimento) ~ '^[0-9]+$'
            THEN trim(chave_externa_diretor_de_atendimento)::int
        ELSE 0
    END AS chave_externa_diretor_de_atendimento,
    CASE
        WHEN trim(chave_externa_diretor) ~ '^[0-9]+$'
            THEN trim(chave_externa_diretor)::int
        ELSE 0
    END AS chave_externa_diretor,
    segmento,
    id_indicador,
    nome_indicador,
    CAST(
        replace(resultado, ',', '.') AS float
    ) AS resultado,
    CAST(
        replace(
            replace(fator, 'NONE', '0'),
            ',', '.'
        ) AS float
    ) AS fator,
    round(
        CAST(
            replace(resultado_calculado, ',', '.') AS numeric
        ),
        3
    ) AS resultado_calculado,
    round(
        CAST(
            replace(percentual_atingimento, ',', '.') AS numeric
        ),
        3
    ) AS percentual_atingimento,
    CAST(
        replace(meta, ',', '.') AS float
    ) AS meta,
    replace(ganho, 'NONE', '0') AS ganho,
    replace(max_ganho, 'NONE', '0') AS max_ganho,
    id_grupo,
    CASE
        WHEN trim(chave_externa_gerente_jr) ~ '^[0-9]+$'
            THEN trim(chave_externa_gerente_jr)::int
        ELSE 0
    END AS chave_externa_gerente_jr,
    CASE
        WHEN trim(chave_externa_gerente_pl) ~ '^[0-9]+$'
            THEN trim(chave_externa_gerente_pl)::int
        ELSE 0
    END AS chave_externa_gerente_pl,
    CASE
        WHEN trim(chave_externa_gerente_sr) ~ '^[0-9]+$'
            THEN trim(chave_externa_gerente_sr)::int
        ELSE 0
    END AS chave_externa_gerente_sr,
    CAST(
        replace(
            replace(fator_2, 'NONE', '0'),
            ',', '.'
        ) AS float
    ) AS fator_2,
    replace(
        replace(fator_3, 'NONE', '0'),
        ',', '.'
    ) AS fator_3,
    replace(
        replace(fator_4, 'NONE', '0'),
        ',', '.'
    ) AS fator_4
FROM public.performance
WHERE data=%s
    and id_indicador <> 86
    and segmento not ilike %s
"""

def get_query_pg(query, indicators):
    if not indicators:
        return query

    placeholders = ", ".join("%s" for _ in indicators)

    return query + f"""
    AND id_indicador IN ({placeholders})
    """