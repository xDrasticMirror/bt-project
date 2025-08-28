import pandas as pd
import os.path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.preprocessing import OneHotEncoder


class RandomForest:
    def __init__(self, base_file_path: str, training_data, draft_model):
        super().__init__()
        self.model_path = base_file_path.format('RandomForest', 'RandomForest', 'model')
        self.encoder_path = base_file_path.format('RandomForest', 'RandomForest', 'encoder')

        self.training_data = training_data
        self.draft_model = draft_model

        self.model, self.encoder = self.load_if_available()
        self.save()

    def save(self) -> None:
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.encoder, self.encoder_path)

    def load_if_available(self, force_training: bool = False) -> tuple:
        if not force_training:
            if os.path.exists(self.model_path) and os.path.exists(self.encoder_path):
                return joblib.load(self.model_path), joblib.load(self.encoder_path)
            else:
                return self.train(), OneHotEncoder(handle_unknown='ignore')
        else:
            return self.train(), OneHotEncoder(handle_unknown='ignore')

    def train(self) -> RandomForestClassifier:
        game_entries = self.encoder.fit_transform(self.training_data[list(self.draft_model.keys())])

        X, y = game_entries, self.training_data['outcome']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) # 0.2

        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        # scores = cross_val_score(self.model, X, y, cv=5)
        # print(f'Cross-val Accuracy:{scores.mean():.4f}')

        cr = classification_report(y_test, y_pred)
        print('Classification report:')
        print(cr)

        print(f'Values: {self.training_data["outcome"].value_counts()}')
        print(f"Model Accuracy: {accuracy * 100:.2f}%")
        return model

    def predict(self, p_data: dict) -> tuple:
        draft = pd.DataFrame([p_data])
        draft_encoded = self.encoder.transform(draft[list(p_data.keys())])

        win_probability = self.model.predict_proba(draft_encoded)  # [:, 1]
        predicted_outcome = self.model.predict(draft_encoded)

        print(f"Model classes: {self.model.classes_}")

        blue_win_probability = win_probability[0][0]
        red_win_probability = win_probability[0][1]

        return blue_win_probability, red_win_probability, predicted_outcome