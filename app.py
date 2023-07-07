import pandas as pd
import uuid
import re
from flask import Flask, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Data Cleaning


def clean_text(text):
    # Convertion en minuscules
    text = text.lower()
    # elimination des retour a la ligne
    text = re.sub('\n', '', text)
    # elimination les symboles
    text = re.sub(r'[^\w\s\t]', '', text)
    # elimination les apostrophes
    text = text.replace("'", "")

    return text


@app.route('/')
# Fonction qui fait le scraping
def scrape():
    # Reviews de Google play
    from google_play_scraper import Sort, reviews_all
    reviews_fr = reviews_all(
        'com.ntech.ijeni1',
        sleep_milliseconds=0,
        lang='fr',
        sort=Sort.NEWEST,
    )
    reviews_eng = reviews_all(
        'com.ntech.ijeni1',
        sleep_milliseconds=0,
        lang='en',
        country='tn',
        sort=Sort.NEWEST,
    )
    reviews_ar = reviews_all(
        'com.ntech.ijeni1',
        sleep_milliseconds=0,
        lang='ar',
        country='tn',
        sort=Sort.NEWEST,
    )
    # Combiner les revues de play store
    reviewsplay = []
    reviewsplay.extend(reviews_fr)
    reviewsplay.extend(reviews_eng)
    reviewsplay.extend(reviews_ar)

    # Creation de dataframe
    df1 = pd.DataFrame(reviewsplay)

    # Ajout d'une colonne source
    df1 = df1.assign(Source='PlayStore')

    # Garder les colonnes necessaires
    df1 = df1[['Source', 'at', 'content', 'score']]

    # Renommer les colonnes
    df1.rename(columns={'at': 'date', 'content': 'review',
               'score': 'rating'}, inplace=True)

    # Reviews de App Store
    from app_store_scraper import AppStore

    # Création d'un object AppStore
    app = AppStore(country='tn', app_name="ijeni", app_id='1547115034')

    # Spécifier les options du scraper
    options = {
        "reviews": True,
        "verbose": True,
    }

    reviews = app.review()
    # Recuperation des revues
    reviewsapp = app.reviews

    # Creation de dataframe
    df2 = pd.DataFrame(reviewsapp)

    # Ajout d'une colonne source
    df2 = df2.assign(Source='AppStore')

    # Garder les colonnes necessaire
    df2 = df2[['Source', 'date', 'review', 'rating']]

    # appliquer la fonction de cleaning
    df2['review'] = df2['review'].astype(str).apply(clean_text)

    # Concatention des deux dataframes de App Store et de Play Store
    df = pd.concat([df1, df2])

    # Reindexer le dataframe
    df.reset_index(drop=True, inplace=True)

    # Ajouter des ID uniques
    df['idRev'] = df.apply(lambda row: uuid.uuid4(), axis=1)

    # Convertion  les timestamps en objets datetime
    df['date'] = pd.to_datetime(df['date'], unit='ms')

    # Passer les résultats en fichier json
    data = df.to_json(orient='records', date_format='iso', default_handler=str)

    with open('dataf.json', 'w') as f:
        f.write(data)

    # Recuperation du contenu du fichier
    with open("dataf.json", 'r') as f:
        data = json.load(f)

    # Itérer le contenu du fichier json
    for item in data:
        # Récupération de la valeur de la clé 'date' et sa convertion en un objet datetime
        item_date_str = item['date']
        item_date = datetime.strptime(item_date_str, '%Y-%m-%dT%H:%M:%S.%f')

    # Convertion de l'objet datetime en un format de date et d'heure convenable fichier JSON
        item['date'] = item_date.strftime('%Y-%m-%d %H:%M:%S')

    # Mettre le résultat final dans un fichier JSON
    with open('reviews.json', 'w') as f:
        json.dump(data, f, indent=4)

    # Insertion du résultat dans la base de données
    import pyodbc
    # Connexion à la base de données
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=ijeni-sqlsdb-prod-westeurope.database.windows.net,1433;DATABASE=ijeni-sqlsdb-test-abirwiem-westeurope;UID=ijeni-admin;PWD=!20ij22@03eni31')
    # Création de curseur pour intéragir avec la base
    cursor = cnxn.cursor()
    # Vider la table avant chaque insertion
    cursor.execute("TRUNCATE TABLE Reviews")

    # Insérer les données du dataframe dans la table Reviews
    for index, row in df.iterrows():
        cursor.execute("INSERT INTO Reviews (Source, date, idRev, rating, review) values (?, ?, ?, ?, ?)",
                       row['Source'], row['date'], row['idRev'], row['rating'], row['review'])
        cnxn.commit()
    # Fermer la connexion
    cnxn.close()

    # Résultat  de l'API sous format JSON
    return jsonify(data)


if __name__ == "_main_":
    app.run()
