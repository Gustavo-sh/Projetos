from flask import Flask, request, jsonify, Response  
import os.path
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import orjson
from flask_compress import Compress


app = Flask(__name__)
Compress(app)


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID_HIERARCHY = "1RL_l7H4s61OPJPSTeVKRKdhp2LKbZXlBltVccgeJeAc"
SAMPLE_RANGE_NAME_HIERARCHY = "Controle_reports!A1:K"

def get_google_sheet_data():
    creds = None

    if os.path.exists(r"G:\Drives compartilhados\MIS_ROBBYSON\ETL\chs\api\token.json"):
        creds = Credentials.from_authorized_user_file(r"G:\Drives compartilhados\MIS_ROBBYSON\ETL\chs\api\token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = service_account.Credentials.from_service_account_file(
                r"G:\Drives compartilhados\MIS_ROBBYSON\ETL\chs\api\credentials.json", 
                scopes=SCOPES
            )
            with open(r"G:\Drives compartilhados\MIS_ROBBYSON\ETL\chs\api\token.json", "w") as token:
                token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result_hier = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_HIERARCHY, range=SAMPLE_RANGE_NAME_HIERARCHY).execute()
        values_hier = result_hier.get("values", [])
        
        if not values_hier:
            print("No data found in hierarchy sheet.")
            return None
        
        df_hier = pd.DataFrame(values_hier[1:], columns=values_hier[0])
        return df_hier
    
    except HttpError as err:
        print(f"An error occurred: {err}")
        return None

def get_db_connection(port):
    df = get_google_sheet_data()
    if df is None:
        return None
    
    #print("Colunas:", df.columns)
    
    try:
        row = df[df['Porta'] == str(port)]
        if row.empty:
            return None

        user = row['User_Bd'].values[0]
        password = row['Pass_Bd'].values[0]
        host = row['IP_interno'].values[0]
        database = "reports"
        cliente = row['NomeCliente'].values[0]
        print(cliente)

        conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        return psycopg2.connect(conn_string)
    except KeyError as e:
        print(f"Coluna não encontrada: {str(e)}")
        return None
    except Exception as e:
        print(f"Erro ao criar a string de conexão: {str(e)}")
        return None

@app.route('/hierarquia', methods=['GET'])
def hierarquia():
    port = request.args.get('port')
    if not port:
        return jsonify({"error": "Porta não fornecida"}), 400

    conn = None
    try:
        conn = get_db_connection(port)
        if conn is None:
            return jsonify({"error": "Conexão ao banco de dados falhou"}), 500

        cursor = conn.cursor()
        query = """
            SELECT DISTINCT 
            extract(year from ar.scaled_date) as ano,
            extract(month from ar.scaled_date) as mes,
            ar.identification as identificacao,
            (case when au.hierarchy_level_id = '1' then 'Nivel 1'  when au.hierarchy_level_id = '0' then 'Sem Informação' else 'Gestor' end) as hierarchy_level,
            ar.hierarchy_level_description as nome_nivel_hierarquia,              
            ar.hierarchies_path_names,
            ar.hierarchies_path_descriptions,
            ar.attributes_path_names,
            ar.attributes_path_descriptions
            FROM public.access_rate ar
            left join active_users au on (au.identification = ar.identification and extract(year from ar.scaled_date) = au."year" and extract(month from ar.scaled_date) = au."month")
            where 
            extract(year from ar.scaled_date) >= 2024
            and extract(month from ar.scaled_date) >= 4
            order by  extract(year from ar.scaled_date),extract(month from ar.scaled_date) desc
        """
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            hierarchies_path_names = results[0][5].split("|")[1:]
            attributes_path_names = results[0][7].split("|")[1:]
            updated_rows = []

            for row in results:
                hierarchies_descriptions = row[6].split("|")[1:]
                attributes_descriptions = row[8].split("|")[1:]

                if len(hierarchies_descriptions) == len(hierarchies_path_names) and len(attributes_descriptions) == len(attributes_path_names):
                    updated_row = list(row[:3]) + hierarchies_descriptions + attributes_descriptions
                    updated_rows.append(updated_row)

            columns = [desc[0] for desc in cursor.description[:3]] + hierarchies_path_names + attributes_path_names
            df = pd.DataFrame(updated_rows, columns=columns)
            return df.to_json(orient="records", force_ascii=False), 200

        return jsonify({"error": "Nenhum dado encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn is not None and not isinstance(conn, str):
            conn.close()

## Resultado
def get_db_connection_string(port):
    df = get_google_sheet_data()
    if df is None:
        return None
    
    try:
        row = df[df['Porta'] == str(port)]
        if row.empty:
            return None

        user = row['User_Bd'].values[0]
        password = row['Pass_Bd'].values[0]
        host = row['IP_interno'].values[0]
        database = "reports"
        conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        return conn_string
    except KeyError as e:
        print(f"Coluna não encontrada: {str(e)}")
        return None
    except Exception as e:
        print(f"Erro ao criar a string de conexão: {str(e)}")
        return None


def calcular_colunas(row, formula_resultado, formula_meta, formula_atingimento):
    # Função de cálculo de colunas (mantida como no exemplo anterior)
    formula_resultado = formula_resultado.replace('resultado', str(row['resultado'])).replace('fator[0]', str(row['factor_0'])).replace('fator[1]', str(row['factor_1'])).replace('fator[2]', str(row['factor_2'])).replace('fator[3]', str(row['factor_3'])).replace('fator[4]', str(row['factor_4']))
    if 'fatorCalculado' in formula_meta:
        row['meta_calculada'] = row['meta']
    else:
        formula_meta = formula_meta.replace('meta', str(row['meta'])).replace('fator[0]', str(row['factor_0'])).replace('fator[1]', str(row['factor_1'])).replace('fator[2]', str(row['factor_2'])).replace('fator[3]', str(row['factor_3'])).replace('fator[4]', str(row['factor_4']))
        try:
            row['meta_calculada'] = eval(formula_meta)

            if row['meta_calculada'] == 1:
               row['meta_calculada'] = row['meta']

        except Exception:
            row['meta_calculada'] = None

    formula_atingimento = formula_atingimento.replace('resultado', str(row['resultado'])).replace('meta', str(row['meta']))
    try:
        row['resultado_calculado'] = eval(formula_resultado)
    except Exception:
        row['resultado_calculado'] = None

    try:
        if formula_atingimento == "0 if meta == -1 else (resultado + 1) / (meta + 1)":
            if row['meta_calculada'] == -1:
                row['atingimento'] = 0
            else:
                row['atingimento'] = (row['resultado_calculado'] + 1) / (row['meta_calculada'] + 1)
        elif formula_atingimento == "0 if resultado == 0 else meta/resultado":
            if row['resultado_calculado'] == 0:
                row['atingimento'] = 0
            else:
                row['atingimento'] = row['meta_calculada'] / row['resultado_calculado']
        elif formula_atingimento == "1 if meta == 0 else resultado/meta":
            if row['meta_calculada'] == 0:
                row['atingimento'] = 1
            else:
                row['atingimento'] = row['resultado_calculado'] / row['meta_calculada']
        elif formula_atingimento == "meta/resultado if resultado > meta else resultado/meta":
            if row['resultado_calculado'] > row['meta_calculada']:
                row['atingimento'] = row['meta_calculada'] / row['resultado_calculado']
            else:
                row['atingimento'] = row['resultado_calculado'] / row['meta_calculada']
        elif formula_atingimento == "10 if resultado == 0 else meta/resultado":
            if row['resultado_calculado'] == 0:
                row['atingimento'] = 10
            else:
                row['atingimento'] = row['meta_calculada'] / row['resultado_calculado']
        else:
            if row['meta_calculada'] == 0 or row['resultado_calculado'] < 0:
                row['atingimento'] = 0
            else:
                row['atingimento'] = row['resultado_calculado'] / row['meta_calculada']
    except Exception:
        row['atingimento'] = None

    return row

def extrair_valores_faixa(faixa):
    faixa = faixa.replace('%', '').replace('à', '-').strip()
    min_val, max_val = faixa.split('-')
    return float(min_val) / 100, float(max_val) / 100

def determinar_nivel(row):
    atingimento_percentual = row['atingimento']
    if row['band_g1_min'] <= atingimento_percentual <= row['band_g1_max']:
        return 1
    elif row['band_g2_min'] <= atingimento_percentual <= row['band_g2_max']:
        return 2
    elif row['band_g3_min'] <= atingimento_percentual <= row['band_g3_max']:
        return 3
    elif row['band_g4_min'] <= atingimento_percentual <= row['band_g4_max']:
        return 4
    else:
        return None

def formatar_resultado(result):
    def format_value(val):
        if val is None or pd.isna(val):
            return None
        if isinstance(val, float) and val.is_integer():
            return int(val)
        elif isinstance(val, float):
            return round(val, 2)
        return val
    
    for row in result:
        row['atingimento'] = format_value(row['atingimento'])
        row['data'] = pd.to_datetime(row['data']).strftime('%Y-%m-%d')
        row['id_nivel'] = int(row['id_nivel']) if not pd.isna(row['id_nivel']) else None
        row['meta_calculada'] = format_value(row['meta_calculada'])
        row['resultado_calculado'] = format_value(row['resultado_calculado'])
        row['semana'] = int(row['semana'])

    return result

def generate_json_stream(df):
    yield '['
    first = True
    for row in df:
        if not first:
            yield ','
        yield orjson.dumps(row).decode('utf-8')
        first = False
    yield ']'

@app.route('/resultado', methods=['GET'])
def calcular():
    port = request.args.get('port')
    if not port:
        return {"error": "Porta não fornecida"}, 400

    conn_string = get_db_connection_string(port)
    if conn_string is None:
        return {"error": "Conexão ao banco de dados falhou"}, 500

    engine = create_engine(conn_string)

    # Carrega as tabelas de indicadores e performance
    df_indicador = pd.read_sql("SELECT id_indicador, formula_resultado, formula_meta, formula_perc_atingimento FROM public.indicador", engine)
    df_performance = pd.read_sql("""
        SELECT 
            cast(date_trunc('month', date) as date) as data, 
            (CASE 
                WHEN extract(day FROM date) = 1 THEN 1 
                WHEN extract(day FROM date) = 8 THEN 2
                WHEN extract(day FROM date) = 15 THEN 3
                WHEN extract(day FROM date) = 22 THEN 4 
                ELSE 5 
             END) AS semana,
            identification, 
            indicator_id, 
            SUM(CAST(REPLACE(result, ',', '.') AS NUMERIC)) AS resultado,
            AVG(CAST(REPLACE(goals, ',', '.') AS NUMERIC)) AS meta,
            SUM(CAST(REPLACE(factor, ',', '.') AS NUMERIC)) AS factor_0,
            SUM(CAST(REPLACE(factor_1, ',', '.') AS NUMERIC)) AS factor_1,
            SUM(CAST(REPLACE(factor_2, ',', '.') AS NUMERIC)) AS factor_2,
            SUM(CAST(REPLACE(factor_3, ',', '.') AS NUMERIC)) AS factor_3,
            SUM(CAST(REPLACE(factor_4, ',', '.') AS NUMERIC)) AS factor_4
        FROM public.performance_week
        where cast(date_trunc('month', date) as date) >= (SELECT cast(date_trunc('month', current_date) - INTERVAL '1 months' as date))
              
        GROUP BY 
            cast(date_trunc('month', date) as date), 
            (CASE 
                WHEN extract(day FROM date) = 1 THEN 1 
                WHEN extract(day FROM date) = 8 THEN 2
                WHEN extract(day FROM date) = 15 THEN 3
                WHEN extract(day FROM date) = 22 THEN 4 
                ELSE 5 
             END),
            identification, 
            indicator_id
    """, engine)

    # Fazendo o merge das duas tabelas
    df_merged = pd.merge(df_performance, df_indicador, left_on='indicator_id', right_on='id_indicador', how='left')

    # Aplicando as fórmulas para calcular as colunas dinâmicas
    df_merged = df_merged.apply(lambda row: calcular_colunas(row, row['formula_resultado'], row['formula_meta'], row['formula_perc_atingimento']), axis=1)

    # Carregando a tabela goals
    df_goals = pd.read_sql("""
        SELECT distinct
            indicator_id,  
            begin_date, 
            end_date, 
            band_g1, 
            band_g2, 
            band_g3, 
            band_g4
        FROM public.goals
        WHERE active = true 
    """, engine)

    # Extraindo os valores mínimos e máximos das faixas
    df_goals['band_g1_min'], df_goals['band_g1_max'] = zip(*df_goals['band_g1'].apply(extrair_valores_faixa))
    df_goals['band_g2_min'], df_goals['band_g2_max'] = zip(*df_goals['band_g2'].apply(extrair_valores_faixa))
    df_goals['band_g3_min'], df_goals['band_g3_max'] = zip(*df_goals['band_g3'].apply(extrair_valores_faixa))
    df_goals['band_g4_min'], df_goals['band_g4_max'] = zip(*df_goals['band_g4'].apply(extrair_valores_faixa))

    # Fazendo o merge com a tabela goals
    df_merged = pd.merge(df_merged, df_goals, on='indicator_id', how='left')

    # Filtrando as datas que estão no range de begin_date e end_date
    df_merged = df_merged[(df_merged['data'] >= df_merged['begin_date']) & (df_merged['data'] <= df_merged['end_date'])]

    # Aplicando a função para determinar o id_nivel
    df_merged['id_nivel'] = df_merged.apply(determinar_nivel, axis=1)

    # Convertendo o resultado para JSON com formatação
    result = df_merged[['data', 'semana', 'identification', 'indicator_id', 'resultado_calculado', 'meta_calculada', 'atingimento', 'id_nivel']].to_dict(orient='records')
    formatted_result = formatar_resultado(result)

    # Retornando o JSON como stream
    return Response(generate_json_stream(formatted_result), content_type='application/json')

if __name__ == '__main__':
    app.run(debug=True)
