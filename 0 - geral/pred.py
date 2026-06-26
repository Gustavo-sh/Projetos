import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

# 1. Carregar base do Excel
df = pd.read_excel("ttt.xlsx")

print(df)

# 2. Separar features (X) e target (y)
X = df.drop(columns=["quantidade"])  # tudo menos a coluna alvo
y = df["quantidade"]  # 1 se comprou, 0 se não

print(X)
print(y)


# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# # 4. Criar e treinar modelo
# modelo = RandomForestClassifier(n_estimators=100, random_state=42)
# modelo.fit(X_train, y_train)

# # 5. Avaliar modelo
# y_pred = modelo.predict(X_test)
# y_proba = modelo.predict_proba(X_test)[:,1]

# print(classification_report(y_test, y_pred))
# print("AUC-ROC:", roc_auc_score(y_test, y_proba))

# # 6. Prever chance de um novo cliente comprar
# novo_cliente = pd.DataFrame({
#     "Idade": [30],
#     "Renda": [4500],
#     "FrequenciaCompras": [12]
# })
# probabilidade = modelo.predict_proba(novo_cliente)[:,1][0]
# print("Chance de compra:", probabilidade)
