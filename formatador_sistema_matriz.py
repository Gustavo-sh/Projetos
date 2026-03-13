import pyodbc
CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"
ATRIBUTES = """
    SET NOCOUNT ON
    select * 
    into #sm
    from sistema_matriz (nolock)
    where periodo = dateadd(d, 1, eomonth(getdate(), -2))

    select av.atributo from #atributos_validos av
    left join #sm sm
    on av.atributo = sm.atributo
    where sm.atributo is null

    drop table #atributos_validos
    drop table #sm
    """

def get_atributes_not_in_sm():
    conn = pyodbc.connect(CONNECTION_STRING)
    cur = conn.cursor()
    cur.execute(ATRIBUTES)
    results = [r[0] for r in cur.fetchall()] 
    cur.close()
    conn.close()
    return results

def main():
    atributes = get_atributes_not_in_sm()
    indicators = [: {"id_nome_indicador": "901 - % DISPONIBILIDADE", "meta": 94, "moedas": 30}, "15 - TEMPO LOGADO", "15 PAUSA NR17"]
    all_rows = []
    for a in atributes:
            for i in indicators:
                row_data = [
                    i,
                    i.get('id_nome_indicador'),
                    meta_val,  
                    i.get('moedas'),
                    i.get('tipo_indicador'),
                    i.get('acumulado'),
                    i.get('esquema_acumulado'),
                    i.get('tipo_matriz'),
                    i.get('data_inicio'),
                    i.get('data_fim'),
                    i.get('periodo'),
                    i.get('escala'),
                    i.get('tipo_de_faturamento'),
                    i.get('descricao'),
                    0,
                    i.get('chamado'),
                    i.get('criterio'),
                    area if area is not None else '',
                    responsavel if responsavel is not None else '',
                    i.get('gerente'),
                    i.get('possui_dmm'),
                    i.get('dmm'),
                    username,
                    data_formatada,
                    0,
                    0,
                    '',
                    0,
                    0,
                    '',
                    0,
                    0,
                    '',
                    i.get('superintendente') or ''
                ]
                all_rows.append(tuple(row_data))