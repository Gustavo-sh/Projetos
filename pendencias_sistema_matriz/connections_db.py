import pyodbc

CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"
CONN = pyodbc.connect(CONNECTION_STRING)

query_part1 = """
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
            (da_qualidade = 0 and da_planejamento = 0) then 'Sem nenhuma validação'
        when
            da_qualidade = 0
            and da_planejamento <> 0
            and da_exop = 0 then 'Qualidade'
        when
            da_qualidade <> 0
            and da_planejamento = 0
            and da_exop = 0 then 'Planejamento'
        when
            da_qualidade <> 0
            and da_planejamento <> 0
            and da_operacao = 0 then 'Operação'
        when
            da_operacao <> 0
            and da_qualidade <> 0
            and da_planejamento <> 0
            and da_exop = 0 then 'Exop'
        else 'N/A'
    end as responsavel
from sistema_matriz (nolock) sm
left join dim.atributo (nolock) a
    on sm.atributo = a.atributo 
left join hmn h
    on sm.atributo = h.atributo
where periodo = dateadd(d, 1, eomonth(GETDATE(), 0))
and (da_operacao = 0 or da_qualidade = 0 or da_planejamento = 0 or da_exop = 0)
)

select isnull(DIRETORATENDIMENTO, 'Sem Diretor') as diretor_atendimento, produto, responsavel, count(atributo) as pendencias
from base
where (atributo like '%porto%' or atributo like '%bradescard%' or atributo like '%quinto%')
"""

query_part2 = """
group by DIRETORATENDIMENTO, produto, responsavel
order by DIRETORATENDIMENTO, produto
"""

def mount_query(arg):
    if arg:
        return query_part1 + arg + query_part2
    return query_part1 + query_part2

def query_results(diretor=None):
    
    cur = CONN.cursor()
    if diretor:
        cur.execute(mount_query(f"and DIRETORATENDIMENTO = '{diretor}'"))
    else:
        cur.execute(mount_query(None))
    resultados = cur.fetchall()
    cur.close()

    return resultados

def get_diretores():
    cur = CONN.cursor()
    cur.execute("""
                with sm as (
                select atributo 
                from sistema_matriz (nolock)
                where periodo = dateadd(d, 1, eomonth(GETDATE(), 0))
                and (atributo like '%porto%' or atributo like '%bradescard%' or atributo like '%quinto%')
                )
                select distinct DIRETORATENDIMENTO 
                from rlt.hmn (nolock) hmn
                inner join sm 
                on hmn.atributo = sm.atributo
                where data = CONVERT(date, getdate()-1) 
                and hmn.atributo is not null 
                and diretor is not null 
                and tipohierarquia = 'operação' 
                and nivelhierarquico = 'operacional'
                """)
    diretores = [row[0] for row in cur.fetchall()]
    cur.close()

    return diretores

def close_connection():
    CONN.close()