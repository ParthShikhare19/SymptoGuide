import os
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from nltk import word_tokenize
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Get the directory where this script is located
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Note: This script requires a CSV file with 'review' and 'result' columns
# The file 'Code_5.csv' should be placed in the same directory as this script
csv_path = os.path.join(_SCRIPT_DIR, "Code_5.csv")

if not os.path.exists(csv_path):
    print(f"Error: File not found: {csv_path}")
    print("Please ensure 'Code_5.csv' exists with 'review' and 'result' columns.")
    exit(1)

data=pd.read_csv(csv_path)
print(data.isnull().sum())

wl=WordNetLemmatizer()

def clean_function(text):
    text = text.lower()
    text=text.replace(".","")
    text= word_tokenize(text)
    text=[t for t in text if t not in punctuation]
    text=[t for t in text if t not in stopwords.words("english")]
    text=[wl.lemmatize(t) for t in text]
    text=",".join(text)
    return(text)

data["clean_review"]=data["review"].apply(clean_function)

tf=TfidfVectorizer()
vector=tf.fit_transform(data["clean_review"])

feature=pd.DataFrame(vector.toarray(),tf.get_feature_names_out())

target=data["result"]

model=MultinomialNB()
model.fit(feature.values,target)

user_review=input("Enter review")
user_review=clean_function(user_review)
v_review=tf.transform(user_review)
res=model.predict(v_review)
print(res)
