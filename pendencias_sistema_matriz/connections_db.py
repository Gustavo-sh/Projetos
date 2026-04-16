import pyodbc

CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"

query = """
with hmn as (
    select distinct 
        atributo, 
        DIRETORATENDIMENTO
    from rlt.hmn (nolock)
    where data = CONVERT(date, getdate()-1)
    and atributo is not null
    and diretor is not null
    and tipohierarquia = 'operação'
    and nivelhierarquico = 'operacional'
)

, base as (
select distinct 
    sm.atributo,
    a.produto,
    da_operacao, 
    da_qualidade, 
    da_planejamento, 
    da_exop,
    DIRETORATENDIMENTO,
    case
        when
            da_operacao = 0 then 'Pendencias Operação'
        when
            da_operacao <> 0
            and da_qualidade = 0
            and da_planejamento <> 0
            and da_exop = 0 then 'Pendencias Qualidade'
        when
            da_operacao <> 0
            and da_qualidade <> 0
            and da_planejamento = 0
            and da_exop = 0 then 'Pendencias Planejamento'
        when
            da_operacao <> 0
            and da_qualidade <> 0
            and da_planejamento <> 0
            and da_exop = 0 then 'Pendencias Exop'
        else 'Pendencias Areas de Apoio'
    end as responsavel
from sistema_matriz (nolock) sm
left join dim.atributo (nolock) a
    on sm.atributo = a.atributo 
left join hmn h
    on sm.atributo = h.atributo
where periodo = dateadd(d, 1, eomonth(GETDATE(), 0))
and (da_operacao = 0 or da_qualidade = 0 or da_planejamento = 0 or da_exop = 0)
)

select isnull(DIRETORATENDIMENTO, 'Sem Diretor'), produto, responsavel, count(atributo) as pendencias
from base
group by DIRETORATENDIMENTO, produto, responsavel
order by DIRETORATENDIMENTO, produto
"""

def query_results():
    conn = pyodbc.connect(CONNECTION_STRING)
    cur = conn.cursor()
    cur.execute(query)
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    return resultados