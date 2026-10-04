import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class NLPService:
    def __init__(self):
        path = Path(__file__).resolve().parent.parent / "ml" / "intents.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        texts, labels = [], []
        for item in data:
            texts.extend(item["examples"])
            labels.extend([item["intent"]] * len(item["examples"]))
        self.vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression(max_iter=1500)
        self.model.fit(X, labels)

    def predict(self, text):
        X = self.vectorizer.transform([text])
        probabilities = self.model.predict_proba(X)[0]
        idx = probabilities.argmax()
        confidence = probabilities[idx]
        intent = self.model.classes_[idx]
        return intent, confidence
