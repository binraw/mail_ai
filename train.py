import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# 1. Chargement des données
# On utilise sep=';' car c'est ce que nous avons défini dans le CSV
df = pd.read_csv('db.csv', sep=';', skiprows=1) # skiprows=1 pour ignorer le "sep=;"

# 2. Nettoyage rapide : on enlève les lignes où le corps ou le topic est vide
df = df.dropna(subset=['body', 'topic'])

# 3. Séparation des données (X = texte, y = étiquette)
X = df['body']
y = df['topic']

# On divise en 80% pour l'entraînement et 20% pour tester la précision
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Création du "Pipeline"
# TfidfVectorizer : transforme le texte en matrice de nombres
# MultinomialNB : l'algorithme de classification (très bon pour le texte)
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# 5. Entraînement !
model.fit(X_train, y_train)

# 6. Sauvegarde du modèle pour l'utiliser plus tard
joblib.dump(model, 'classificateur_emails.pkl')

print(f"Modèle entraîné avec succès ! Précision : {model.score(X_test, y_test):.2%}")