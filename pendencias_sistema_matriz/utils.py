from dateutil.relativedelta import relativedelta
from datetime import datetime

def mount_message(resultados):
    if not resultados:
        return "Sem pendências hoje ✅"

    hoje = datetime.today()
    primeiro_dia_atual = hoje.replace(day=1)
    primeiro_dia_proximo = primeiro_dia_atual + relativedelta(months=1)
    dias = (primeiro_dia_proximo - hoje).days

    msg = f"🚀 Sistema Matriz - Mensagem automática 🚀\n\n⏰ Faltam {dias} dias para o fim do prazo!\n\n"
    pendencias = ""

    diretor_atual = None
    produto_atual = None
    resp_qtd = {"Pendencias Operação": 0, "Pendencias Qualidade": 0, "Pendencias Planejamento": 0, "Pendencias Exop": 0, "Pendencias Areas de Apoio": 0}

    for diretor, produto, responsavel, qtd in resultados:
        resp_qtd[responsavel] += qtd
        if diretor != diretor_atual:
            pendencias += f"\n🔹 {diretor}\n"
            diretor_atual = diretor
        if produto != produto_atual:
            pendencias += f"   --- *{produto}*\n"
            produto_atual = produto
        pendencias += f"   -- {responsavel}: {qtd}\n"

    total = sum(resp_qtd.values())
    msg += f"🧾 Total de pendências: {total}\n\n"

    msg += "👤 Pendências Por Responsável: \n\n"

    for chave, valor in resp_qtd.items():
        msg += f"{chave}: {valor}\n"

    msg += "\n📊 Pendências por diretor e produto:\n"

    msg += pendencias

    return msg
