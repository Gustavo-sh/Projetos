from dateutil.relativedelta import relativedelta
from datetime import datetime

def mount_message(resultados):
    hoje = datetime.today()
    primeiro_dia_atual = hoje.replace(day=1)
    primeiro_dia_proximo = primeiro_dia_atual + relativedelta(months=1)
    dias = (primeiro_dia_proximo - hoje).days

    msg = f"🚀 Sistema Matriz - Mensagem automática 🚀\n\n⏰ Faltam {dias} dias para o fim do prazo!\n\n"
    pendencias = ""

    if not resultados:
        return msg + "Sem pendências hoje ✅"

    diretor_atual = None
    produto_atual = None
    resp_qtd = {"Pendencias Apoio": 0, "Pendencias Qualidade": 0, "Pendencias Planejamento": 0, "Pendencias Operação": 0, "Pendencias Exop": 0}

    for diretor, produto, responsavel, qtd in resultados:
        if produto != produto_atual:
            pendencias += f"\n   ⚫ *{produto}*\n"
            produto_atual = produto
        resp_qtd[responsavel] += qtd
        if diretor != diretor_atual:
            pendencias += f"\n🔹 {diretor}\n"
            diretor_atual = diretor
        
        pendencias += f"\n   - {responsavel}: {qtd}\n"

    total = sum(resp_qtd.values())
    msg += f"🧾 Total de pendências: {total}\n\n"

    msg += "👤 Pendências Por Responsável: \n\n"

    for chave, valor in resp_qtd.items():
        msg += f"{chave}: {valor}\n"

    msg += "\n📊 Pendências por produto e diretor:\n"

    msg += pendencias

    return msg

def mount_message_director(resultados, diretor):
    hoje = datetime.today()
    primeiro_dia_atual = hoje.replace(day=1)
    primeiro_dia_proximo = primeiro_dia_atual + relativedelta(months=1)
    dias = (primeiro_dia_proximo - hoje).days

    msg = f"🚀 Sistema Matriz - Mensagem automática 🚀\n\n⏰ Faltam {dias} dias para o fim do prazo!\n\n"
    pendencias = f"\n🔹 {diretor}\n"
    if not resultados:
        return msg + "Sem pendências hoje ✅"

    produto_atual = None
    resp_qtd = {"Pendencias Apoio": 0, "Pendencias Qualidade": 0, "Pendencias Planejamento": 0, "Pendencias Operação": 0, "Pendencias Exop": 0}

    for _, produto, responsavel, qtd in resultados:
        if produto != produto_atual:
            pendencias += f"\n   ⚫ *{produto}*\n\n"
            produto_atual = produto
        resp_qtd[responsavel] += qtd
        pendencias += f"   - {responsavel}: {qtd}\n"

    total = sum(resp_qtd.values())
    msg += f"🧾 Total de pendências: {total}\n\n"

    msg += "👤 Pendências Por Responsável: \n\n"

    for chave, valor in resp_qtd.items():
        msg += f"{chave}: {valor}\n"

    msg += "\n📊 Pendências por produto e diretor:\n"

    msg += pendencias

    return msg