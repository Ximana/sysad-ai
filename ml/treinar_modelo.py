# Importar bibliotecas
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import pickle

# Carregar dados
data = pd.read_csv('heart_disease_data.csv')

# Separar features e target
X = data.drop('target', axis=1)
y = data['target']

# Dividir os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Escalonar os dados
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Modelo Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# Modelo Gradient Boosting
gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
gb_model.fit(X_train_scaled, y_train)

# Salvar os modelos e o scaler
with open('rf_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)
with open('gb_model.pkl', 'wb') as f:
    pickle.dump(gb_model, f)
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
    
