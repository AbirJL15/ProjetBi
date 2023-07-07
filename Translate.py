import pandas as pd
import json
import re
from deep_translator import GoogleTranslator

# Fonction de nettoyage de texte


def clean_text(text):
    # Convertion en minuscules
    text = text.lower()
    # elimination des retour a la ligne
    text = re.sub('\n', '', text)
    # elimination des symboles
    text = re.sub(r'[^\w\s\t]', '', text)
    text = text.replace("'", "")
    return text


# Création de dictionnaire tunisien-français
TN_dict = {
    'jarebtha': 'tester',
    'jarabtha': 'tester',
    '3ejbetni': 'aimer',
    'w': 'et',
    'el': 'le',
    'ywaf9kom': 'courage',
    'mochkla': 'probleme',
    'tasjil': 'inscription',
    'nsajel': 'inscription',
    'cod': 'code',
    'youselch': 'bloquer',
    'yt3adache': 'bloquer',
    'temchich': 'bloquer',
    'najamtech': 'bloquer',
    '7abech': 'bloquer',
    'bel': 'avec',
    'tsal7o': 'reparation',
    'sal7ouh': 'reparation',
    'b1': 'bien',
    'mezyena': 'magnifique',
    'tayara': 'excellente',
    'heyla': 'excellente',
    'mzyana': 'magnifique',
    'mzyena': 'magnifque',
    'ta7founa': 'bonne',
    'hlowa': 'bonne',
    'behye': 'bonne',
    'ma7leha': 'bonne',
    'tayaraaa': 'excellente',
    'tenja7': 'magnifique',
    'ness': 'client',
    'mocharkin': 'client',
    'tista3milha': 'utiliser',
    'lfekra': 'idee',
    'fekra': 'idee',
    'barcha': 'beaucoup',
    'yasr': 'tres',
    'yesser': 'tres',
    'yeser': 'tres',
    'beug': 'bug',
    'rzinaaaaaaa': 'bug',
    'thkila': 'bug',
    'zbelaaa': 'mauvaise',
    'ya3tikoum': 'bravo',
    'ya3tikom': 'bravo',
    'yaatikom': 'bravo',
    'nas7ouni': 'recommander',
    'fergha': 'vide',
    'mafiha': 'vide',
    'ma': 'ne pas',
    'Ma': 'ne pas',
    'chay': 'rien',
    'isa7a': 'bravo',
    'saha': 'bravo',
    'yaatikom': 'bravo',
    'zebi': ' ',
    'Saha': 'bravo',
    'رزينة': 'lente',
    'راءع': 'magnifique',
    'نشالله': 'souhaite',
    'مربوحة': 'bon courage',
    'ale5r': 'very',
    'behy': 'bonne',
    'حاول': 'essayer',
    'تطور': 'évulotion',
    'في': 'de',
    'خط': 'écriture',
    'عربي': 'arabe',
    'طيارة': 'magnifique',
    'برافو': 'bravo',
    'يعطيكم': 'bravo',
    'الصحة': 'bravo',
    'حلوة': 'magnifique',
    'حلو': 'bon',
    'فكرة': 'idee',
    'المشكلة': 'probleme',
    'titcrasha': 'bug',
    'lkol': 'tous',
    'يا': 'oh',
    ' ربي': 'dieu'


}


# Mettre le dictionnaire dans un dataframe
df = pd.DataFrame(list(TN_dict.items()), columns=['Mot', 'Synonymes'])

# Convertir le dictionnaire en CSV
df.to_csv('Dict_TN.csv', index=False)

# Ouvrir dictionnaire
df_synonymes = pd.read_csv('Dict_TN.csv', index_col=0)

# Recuperer le fichier JSON des revues scrapées
with open('reviews.json', 'r') as f:
    data = json.load(f)

commentaires_traduits = []
# Traduction à partir du dictionnaire tunisien
for d in data:

    commentaire = d['review']
    commentaire_clean = clean_text(commentaire)
    mots = commentaire_clean.split()
    mots_traduits = []
    for mot in mots:
        if mot in df_synonymes.index:
            mots_traduits.extend(df_synonymes.loc[mot])
        else:
            mots_traduits.append(mot)
    commentaire_traduit = ' '.join(mots_traduits)
    d['review'] = commentaire_traduit
    commentaires_traduits.append(d)

# Enregistrement des commentaires modifiés dans un nouveau fichier JSON
with open('reviews_etat1.json', 'w', encoding='utf-8') as f:
    json.dump(commentaires_traduits, f, ensure_ascii=False, indent=4)


# Ouvrir le fichier JSON
with open('reviews_etat1.json', encoding='utf-8') as f:
    data = json.load(f)

# Traduction des commentaires en anglais
for item in data:
    review = item['review']
    translation = GoogleTranslator(
        source='auto', target='en').translate(review)
    item['review'] = translation

# Enregistrement des commentaires après traduction dans un fichier JSON
with open('reviews_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
