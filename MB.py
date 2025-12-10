import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from nltk import word_tokenize
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

data=pd.read_csv("Code_5.csv")
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
