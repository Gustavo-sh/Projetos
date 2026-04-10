import time
import pyodbc
import pandas as pd
import numpy as np 
from datetime import datetime, timedelta

BASE = """
        SET NOCOUNT ON;
        SET XACT_ABORT ON;

        IF OBJECT_ID('tempdb..#atributos') IS NOT NULL DROP TABLE #atributos;
        IF OBJECT_ID('tempdb..#tipos_indicadores') IS NOT NULL DROP TABLE #tipos_indicadores;
        IF OBJECT_ID('tempdb..#formatos_indicadores') IS NOT NULL DROP TABLE #formatos_indicadores;
        IF OBJECT_ID('tempdb..#agg') IS NOT NULL DROP TABLE #agg;
        IF OBJECT_ID('tempdb..#base') IS NOT NULL DROP TABLE #base;

        -- Capturar nomes dos atributos

        SELECT atributo, id 
        INTO #atributos
        FROM dbo.dim_atributo (NOLOCK)

        -- Capturar tipos dos indicadores

        SELECT 
            id_indicador,
            case when formula_perc_atingimento like '%meta/resultado%' then 'Menor Melhor'
            when formula_perc_atingimento like '%resultado/meta%' then 'Maior Melhor'
            when formula_perc_atingimento is null then 'Nenhum'
            else 'Maior Melhor' end as tipo
        INTO #tipos_indicadores
        FROM rby.indicador (NOLOCK)
        where formula_perc_atingimento is not null

        -- Capturar formatos dos indicadores

        select id_indicador, case when formato = 'coin' then 'integer' else formato end as formato 
        into #formatos_indicadores
        from rby_indicador (nolock) 
        where formato is not null

        -- Gerar dados agregados

        SELECT
            id,
            id_segmento,
            chave_externa,
            formula_resultado,
            formula_meta,
            formula_atingimento,

            SUM(resultado)  AS s_resultado,
            SUM(fator)      AS s_fator,
            SUM(fator_2)    AS s_fator2,
            SUM(fator_3)    AS s_fator3,
            SUM(fator_4)    AS s_fator4,
            SUM(meta)       AS s_meta,
            SUM(hc)         AS s_hc

        INTO #agg
        FROM rlt.bussola (NOLOCK)
        WHERE data BETWEEN DATEADD(D,1,EOMONTH(GETDATE(),-2)) AND EOMONTH(GETDATE(),-1)
        AND id not in (6,34,15,48,49)
        and id not in (select id_indicador from rby.indicador (nolock) where formula_meta not like '%fatorCalc%' and formula_meta not like '%meta%' and indicador_nome <> 'Descontinuado')
        AND id not in (select distinct id_indicador from rby.indicador (nolock) where indicador_nome like '%pausa%')
        GROUP BY
            id,
            id_segmento,
            chave_externa,
            formula_resultado,
            formula_meta,
            formula_atingimento


        -- Gerar resultado e meta calculado

        SELECT
            id AS id_indicador,
            id_segmento,
            chave_externa,
            formula_atingimento,

            CASE 
                WHEN formula_resultado = 2 THEN s_resultado
                WHEN formula_resultado = 3 THEN iif(s_fator = 0, 0, s_resultado / s_fator)
                WHEN formula_resultado = 5 THEN (s_resultado / s_fator) - (s_fator2 / s_fator3)
                WHEN formula_resultado = 6 THEN iif(s_fator2 = 0, 0, s_resultado / s_fator2)
                WHEN formula_resultado = 7 THEN IIF(s_fator = 0,0,s_fator / s_resultado)
                WHEN formula_resultado = 8 THEN 1 - (s_resultado / s_fator)
                WHEN formula_resultado = 9 THEN ((s_resultado / s_fator2) - (s_fator2 / s_fator3)) * 100
                WHEN formula_resultado = 10 THEN (s_resultado / s_fator) + (s_fator2 / s_fator3)
                WHEN formula_resultado = 11 THEN IIF((s_fator = 0 OR s_fator4 > s_fator),0,(s_resultado/(s_fator2/s_fator))*(1-(s_fator3/s_fator)))
                WHEN formula_resultado = 12 THEN (s_resultado - s_fator) / s_fator2
                WHEN formula_resultado = 13 THEN (s_resultado / s_fator) - (s_fator2 / s_fator)
            END AS resultado,

            CASE
                WHEN formula_meta = 1  THEN s_meta
                WHEN formula_meta = 2  THEN iif(s_fator2 = 0,0,s_fator / s_fator2)
                WHEN formula_meta = 3  THEN s_fator4
                WHEN formula_meta = 4  THEN IIF(s_fator3 = 0,0,s_fator4 / s_fator3)
                WHEN formula_meta = 5  THEN IIF(s_hc = 0,0,s_meta / s_hc)
                WHEN formula_meta = 6  THEN s_fator2
                WHEN formula_meta = 7  THEN IIF(s_fator = 0,0,s_meta / s_fator)
                WHEN formula_meta = 8  THEN IIF(s_fator2 = 0,0,s_meta / s_fator2)
                WHEN formula_meta = 9  THEN IIF(s_fator4 = 0,0,s_meta / s_fator4)
                WHEN formula_meta = 10 THEN IIF(s_fator = 0,0,s_fator2 / s_fator)
                WHEN formula_meta = 11 THEN IIF(s_fator3 = 0,0,s_fator2 / s_fator3)
            END AS meta

        INTO #base
        FROM #agg

        -- Query final

        SELECT
            a.atributo,
            b.id_indicador,
            chave_externa AS operador,
            resultado,
            meta,
            formula_atingimento,
            g1,
            g2,
            g3,
            t.tipo,
            ti.formato,
            faixa_inferior,
            faixa_superior
        FROM #base b
        JOIN #atributos a ON b.id_segmento = a.id
        LEFT JOIN dbo.faixa_grupos f 
            ON f.Id_Indicador = b.id_indicador
            AND f.data = EOMONTH(GETDATE(), -1)
        LEFT JOIN #tipos_indicadores t
            ON b.id_indicador = t.id_indicador
        left join #formatos_indicadores ti
            on b.id_indicador = ti.id_indicador
        left join faixas_meta_smart (nolock) fms
            on b.id_indicador = fms.id

        drop table #atributos
        drop table #tipos_indicadores
        drop table #formatos_indicadores
        drop table #agg
        drop table #base
    """

CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;Timeout=60;"

def get_base():
    conn = pyodbc.connect(CONNECTION_STRING)
    df = pd.read_sql(BASE, conn)
    conn.close()
    return df

def insert_result(df):

    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    insert_sql = """
    INSERT INTO dbo.meta_smart (
        data_referencia,
        data_insert,
        atributo,
        id_indicador,
        meta_smart,
        meta_original,
        p_g1g2,
        tipo_meta
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    dados = [
        (
            row.data_referencia,
            row.data_insert,
            row.atributo,
            row.id_indicador,
            row.meta_otimizada,
            row.meta_original,
            row.p_g1g2,
            row.tipo_meta
        )
        for row in df.itertuples(index=False)
    ]

    cursor.execute("DELETE FROM dbo.meta_smart WHERE data_referencia = dateadd(d, 1, eomonth(getdate(), -2))")
    cursor.fast_executemany = True
    cursor.executemany(insert_sql, dados)

    conn.commit()
    cursor.close()
    conn.close()

def calc_p_g1g2(df, meta):

    resultado = df["resultado"].to_numpy()
    formula = df["formula_atingimento"].to_numpy()
    g1 = df["g1"].to_numpy()
    g2 = df["g2"].to_numpy()
    g3 = df["g3"].to_numpy()

    ating = np.zeros_like(resultado, dtype=float)

    mask = formula == 2
    ating[mask] = np.where(resultado[mask] == 0, 10, meta / resultado[mask])

    mask = formula == 3
    cond = (meta == 0) | (resultado[mask] <= 0)
    ating[mask] = np.where(cond, 0, resultado[mask] / meta)

    mask = formula == 4
    ating[mask] = np.where(
        resultado[mask] > meta,
        meta / resultado[mask],
        resultado[mask] / meta
    )

    mask = formula == 6
    ating[mask] = np.where(
        meta == -1,
        0,
        (resultado[mask] + 1) / (meta + 1)
    )

    mask = formula == 7
    ating[mask] = np.where(
        meta > 0.00001,
        resultado[mask] / meta,
        np.where(resultado[mask] == 0, 1, resultado[mask] / meta)
    )

    mask = formula == 8
    r = resultado[mask] / meta
    ating[mask] = np.where(r >= 1, 0, r)

    mask = formula == 9
    ating[mask] = np.where(resultado[mask] >= 0, 10, meta / resultado[mask])

    grupo = np.where(
        ating < g3, 4,
        np.where(
            ating < g2, 3,
            np.where(
                ating < g1, 2,
                1
            )
        )
    )

    return np.mean(grupo <= 2)

def calc_ating_medio(df, meta):

    resultado = df["resultado"].to_numpy()
    formula = df["formula_atingimento"].to_numpy()

    ating = np.zeros_like(resultado, dtype=float)

    mask = formula == 2
    ating[mask] = np.where(resultado[mask] == 0, 10, meta / resultado[mask])

    mask = formula == 3
    cond = (meta == 0) | (resultado[mask] <= 0)
    ating[mask] = np.where(cond, 0, resultado[mask] / meta)

    mask = formula == 4
    ating[mask] = np.where(
        resultado[mask] > meta,
        meta / resultado[mask],
        resultado[mask] / meta
    )

    mask = formula == 6
    ating[mask] = np.where(
        meta == -1,
        0,
        (resultado[mask] + 1) / (meta + 1)
    )

    mask = formula == 7
    ating[mask] = np.where(
        meta > 0.00001,
        resultado[mask] / meta,
        np.where(resultado[mask] == 0, 1, resultado[mask] / meta)
    )

    mask = formula == 8
    r = resultado[mask] / meta
    ating[mask] = np.where(r >= 1, 0, r)

    mask = formula == 9
    ating[mask] = np.where(resultado[mask] >= 0, 10, meta / resultado[mask])

    return np.mean(ating)

def metodo_variacao(df, meta):
    atingimento = calc_ating_medio(df, meta)
    tipo = df.tipo.iloc[0]
    id_indicador = int(df.id_indicador.iloc[0])
    nova_meta = None

    if tipo == "Maior Melhor":
        if atingimento >= 1:
            nova_meta = meta + (meta * 0.03)
            if id_indicador == 901 and nova_meta > 0.98:
                nova_meta = 0.98
            return nova_meta 
        else:
            nova_meta = meta - (meta * 0.03)
            if id_indicador == 901 and nova_meta < 0.90:
                nova_meta = 0.90
            return nova_meta
    else:
        if atingimento >= 1:
            return meta - (meta * 0.03)
        else:
            return meta + (meta * 0.03)

def encontrar_meta(df):

    meta_original = df.meta.iloc[0]
    tipo = df.tipo.iloc[0]

    faixa_inf = df.faixa_inferior.iloc[0]
    faixa_sup = df.faixa_superior.iloc[0]

    if pd.isna(faixa_inf):
        faixa_inf = 0.37

    if pd.isna(faixa_sup):
        faixa_sup = 0.43

    p_original = calc_p_g1g2(df, meta_original)
    if faixa_inf <= p_original <= faixa_sup:
        return meta_original, p_original, "Original", meta_original
    
    low = meta_original * 0.01
    high = meta_original * 100

    for _ in range(20):

        meta = (low + high) / 2
        p = calc_p_g1g2(df, meta)

        if faixa_inf <= p <= faixa_sup:
            if abs((meta - meta_original) / meta_original) > 0.03:
                meta_variacao = metodo_variacao(df, meta_original)
                p_variacao = calc_p_g1g2(df, meta_variacao)
                return meta_variacao, p_variacao, "Variação", meta_original
            return meta, p, "P_G1G2", meta_original

        if p < faixa_inf:
            if tipo == "Maior Melhor":
                high = meta
            else:
                low = meta

        elif p > faixa_sup:
            if tipo == "Maior Melhor":
                low = meta
            else:
                high = meta

    meta_variacao = metodo_variacao(df, meta_original)
    p_variacao = calc_p_g1g2(df, meta_variacao)

    return meta_variacao, p_variacao, "Variação", meta_original

def main():
    start_query = time.time()
    df = get_base()
    
    print("df gerado, query executada em ", (time.time() - start_query))

    resultados = []
    print("total de linhas para iterar: ", len(df.groupby(["id_indicador","atributo"])))

    start_for = time.time()
    for (indicador, atributo), grupo in df.groupby(["id_indicador","atributo"]):

        meta_otima, p, tipo_meta, meta_original = encontrar_meta(grupo)
        formato = grupo.formato.iloc[0]

        faixa_inf = grupo.faixa_inferior.iloc[0]
        faixa_sup = grupo.faixa_superior.iloc[0]

        if pd.isna(faixa_inf):
            faixa_inf = 0.37

        if pd.isna(faixa_sup):
            faixa_sup = 0.43

        if formato == "integer":
            meta_otima = round(meta_otima)
            p = calc_p_g1g2(grupo, meta_otima)
        elif formato == "hour":
            meta_otima = meta_otima/86400
            meta_original = meta_original/86400
        elif formato == "percentage":
            meta_otima = meta_otima*100
            meta_original = meta_original*100

        resultados.append({
            "atributo": atributo,
            "id_indicador": indicador,
            "meta_otimizada": meta_otima,
            "meta_original": meta_original,
            "p_g1g2": p,
            "tipo_meta": tipo_meta
        })

    print("for executado em ", (time.time() - start_for))
    resultado_final = pd.DataFrame(resultados)

    hoje = datetime.now()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    data_referencia = (primeiro_dia_mes_atual - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
    data_insert = hoje.strftime("%Y-%m-%d")

    resultado_final.insert(0, "data_insert", data_insert)
    resultado_final.insert(0, "data_referencia", data_referencia)

    arquivo_saida = "meta_smart.xlsx"

    resultado_final.to_excel(
        arquivo_saida,
        index=False
    )

    insert_result(resultado_final)

if __name__ == "__main__":
    main()