import time
import pyodbc
import pandas as pd
import numpy as np 

BASE = """
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    SELECT atributo, id 
    INTO #atributos
    FROM dbo.dim_atributo (NOLOCK)

    SELECT 
        id_indicador,
        case when formula_perc_atingimento like '%meta/resultado%' then 'Menor Melhor'
        when formula_perc_atingimento like '%resultado/meta%' then 'Maior Melhor'
        when formula_perc_atingimento is null then 'Nenhum'
        else 'Maior Melhor' end as tipo
    INTO #tipos_mm
    FROM rby.indicador (NOLOCK)
    where formula_perc_atingimento is not null

    select id_indicador, case when formato = 'coin' then 'integer' else formato end as formato 
    into #tipos_ind
    from rby_indicador (nolock) 
    where formato is not null

    select distinct id_segmento, chave_externa
    into #hc
    from rlt.bussola (nolock) 
    where data BETWEEN DATEADD(D,1,EOMONTH(GETDATE(),-2)) AND EOMONTH(GETDATE(),-1)

    select id_segmento
    into #segmentos
    from #hc
    group by id_segmento
    having COUNT(chave_externa) > 5

    /* 1️⃣ AGREGAÇÃO (SUM feito apenas uma vez) */

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
    AND id_segmento in (select id_segmento from #segmentos)
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


    /* 2️⃣ APLICAR AS FÓRMULAS */

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
    LEFT JOIN #tipos_mm t
        ON b.id_indicador = t.id_indicador
    left join #tipos_ind ti
        on b.id_indicador = ti.id_indicador
    left join faixas_meta_smart fms
        on b.id_indicador = fms.id

    drop table #atributos
    drop table #tipos_mm
    drop table #tipos_ind
    drop table #agg
    drop table #base
    drop table #hc
    drop table #segmentos
    """

CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"

def get_base():
    conn = pyodbc.connect(CONNECTION_STRING)
    df = pd.read_sql(BASE, conn)
    conn.close()
    return df

def calc_ating(resultado, meta, formula):

    if formula == 2:
        return 10 if resultado == 0 else meta / resultado

    if formula == 3:
        if meta == 0 or resultado <= 0:
            return 0
        return resultado / meta

    if formula == 4:
        return meta / resultado if resultado > meta else resultado / meta

    if formula == 6:
        return 0 if meta == -1 else (resultado + 1) / (meta + 1)

    if formula == 7:
        if meta > 0.00001:
            return resultado / meta
        return 1 if resultado == 0 else resultado / meta

    if formula == 8:
        r = resultado / meta
        return 0 if r >= 1 else r

    if formula == 9:
        return 10 if resultado >= 0 else meta / resultado

    return 0

def calc_grupo(ating, g1, g2, g3):

    if ating < g3:
        return 4
    elif ating < g2:
        return 3
    elif ating < g1:
        return 2
    else:
        return 1

def calc_p_g1g2(df, meta):

    resultado = df["resultado"].to_numpy()
    formula = df["formula_atingimento"].to_numpy()
    g1 = df["g1"].to_numpy()
    g2 = df["g2"].to_numpy()
    g3 = df["g3"].to_numpy()

    ating = np.zeros_like(resultado, dtype=float)

    # formula 2
    mask = formula == 2
    ating[mask] = np.where(resultado[mask] == 0, 10, meta / resultado[mask])

    # formula 3
    mask = formula == 3
    cond = (meta == 0) | (resultado[mask] <= 0)
    ating[mask] = np.where(cond, 0, resultado[mask] / meta)

    # formula 4
    mask = formula == 4
    ating[mask] = np.where(
        resultado[mask] > meta,
        meta / resultado[mask],
        resultado[mask] / meta
    )

    # formula 6
    mask = formula == 6
    ating[mask] = np.where(
        meta == -1,
        0,
        (resultado[mask] + 1) / (meta + 1)
    )

    # formula 7
    mask = formula == 7
    ating[mask] = np.where(
        meta > 0.00001,
        resultado[mask] / meta,
        np.where(resultado[mask] == 0, 1, resultado[mask] / meta)
    )

    # formula 8
    mask = formula == 8
    r = resultado[mask] / meta
    ating[mask] = np.where(r >= 1, 0, r)

    # formula 9
    mask = formula == 9
    ating[mask] = np.where(resultado[mask] >= 0, 10, meta / resultado[mask])

    # cálculo de grupo vetorizado
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

def encontrar_meta(df):

    meta_original = df.meta.iloc[0]
    tipo = df.tipo.iloc[0]

    faixa_inf = df.faixa_inferior.iloc[0]
    faixa_sup = df.faixa_superior.iloc[0]
    if pd.isna(faixa_inf):
        faixa_inf = 0.37

    if pd.isna(faixa_sup):
        faixa_sup = 0.43
    
    alvo = (faixa_inf + faixa_sup) / 2

    low = meta_original * 0.01
    high = meta_original * 100

    melhor_meta = meta_original
    melhor_p = calc_p_g1g2(df, meta_original)
    melhor_erro = abs(melhor_p - alvo)

    for _ in range(20):

        meta = (low + high) / 2
        p = calc_p_g1g2(df, meta)

        erro = abs(p - alvo)

        if erro < melhor_erro:
            melhor_meta = meta
            melhor_p = p
            melhor_erro = erro

        if faixa_inf <= p <= faixa_sup:
            return meta, p

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

    return melhor_meta, melhor_p

def calc_ating_medio(df, meta):

    resultado = df["resultado"].to_numpy()
    formula = df["formula_atingimento"].to_numpy()

    ating = np.zeros_like(resultado, dtype=float)

    # formula 2
    mask = formula == 2
    ating[mask] = np.where(resultado[mask] == 0, 10, meta / resultado[mask])

    # formula 3
    mask = formula == 3
    cond = (meta == 0) | (resultado[mask] <= 0)
    ating[mask] = np.where(cond, 0, resultado[mask] / meta)

    # formula 4
    mask = formula == 4
    ating[mask] = np.where(
        resultado[mask] > meta,
        meta / resultado[mask],
        resultado[mask] / meta
    )

    # formula 6
    mask = formula == 6
    ating[mask] = np.where(
        meta == -1,
        0,
        (resultado[mask] + 1) / (meta + 1)
    )

    # formula 7
    mask = formula == 7
    ating[mask] = np.where(
        meta > 0.00001,
        resultado[mask] / meta,
        np.where(resultado[mask] == 0, 1, resultado[mask] / meta)
    )

    # formula 8
    mask = formula == 8
    r = resultado[mask] / meta
    ating[mask] = np.where(r >= 1, 0, r)

    # formula 9
    mask = formula == 9
    ating[mask] = np.where(resultado[mask] >= 0, 10, meta / resultado[mask])

    return np.mean(ating)

def encontrar_meta_atingimento(df):

    meta_original = df.meta.iloc[0]
    tipo = df.tipo.iloc[0]

    low = meta_original * 0.01
    high = meta_original * 100

    melhor_meta = meta_original
    melhor_erro = abs(calc_ating_medio(df, meta_original) - 1)

    for _ in range(20):

        meta = (low + high) / 2

        ating = calc_ating_medio(df, meta)

        erro = abs(ating - 1)

        if erro < melhor_erro:
            melhor_meta = meta
            melhor_erro = erro

        if 0.98 <= ating <= 1.02:
            return meta

        if tipo == "Maior Melhor":
            if ating > 1:
                low = meta
            else:
                high = meta
        else:
            if ating > 1:
                high = meta
            else:
                low = meta

    return melhor_meta

def main():
    start_query = time.time()
    df = get_base()
    
    print("df gerado, query executada em ", (time.time() - start_query))

    resultados = []
    print("total de linhas para iterar: ", len(df.groupby(["id_indicador","atributo"])))

    start_for = time.time()
    for (indicador, atributo), grupo in df.groupby(["id_indicador","atributo"]):
        meta_critica = False
        meta_otima, p = encontrar_meta(grupo)
        faixa_inf = grupo.faixa_inferior.iloc[0]
        faixa_sup = grupo.faixa_superior.iloc[0]
        if pd.isna(faixa_inf):
            faixa_inf = 0.37

        if pd.isna(faixa_sup):
            faixa_sup = 0.43
        if p < faixa_inf * 0.5 or p > faixa_sup * 1.5:
            meta_critica = True
            meta_otima = encontrar_meta_atingimento(grupo)
            p = calc_p_g1g2(grupo, meta_otima)
        
        # 🔹 ajuste de formato da meta
        formato = grupo.formato.iloc[0]

        if formato == "integer":
            meta_otima = round(meta_otima)
            p = calc_p_g1g2(grupo, meta_otima)

        definicao = None
        if faixa_inf <= p <= faixa_sup:
            definicao = "otima"
        elif p > faixa_sup and p < (faixa_sup * 1.5):
            definicao = "alto aceitavel"
        elif p < faixa_inf and p > (faixa_inf * 0.5):
            definicao = "baixo aceitavel"
        else:
            definicao = "critico estrutural"
        resultados.append({
            "id_indicador": indicador,
            "atributo": atributo,
            "meta_otima": meta_otima,
            "p_g1g2": p,
            "tipo_meta": "Atingimento" if meta_critica else "P_G1G2",
            "definicao": definicao
        })

    print("for executado em ", (time.time() - start_for))
    resultado_final = pd.DataFrame(resultados)

    arquivo_saida = "metas_otimizadas.xlsx"

    resultado_final.to_excel(
        arquivo_saida,
        index=False
    )


if __name__ == "__main__":
    main()