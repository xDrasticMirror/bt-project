import pandas as pd
import os.path
import joblib

from xgboost import XGBClassifier

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report


class XGBoost:
    def __init__(self, base_file_path: str, training_data, draft_model):
        super().__init__()
        self.model_path = base_file_path.format('XGBoost', 'XGBoost', 'model')
        self.feature_path = base_file_path.format('XGBoost', 'XGBoost', 'features')

        self.training_data = training_data
        self.draft_model = draft_model

        self.model = None
        self.feature_names = None
        self.label_encoder = None
        self.X_test = None
        self.y_test = None

        self.model, self.feature_names = self.load_if_available()
        self.save()

    def debug(self) -> None:
        if self.X_test is None or self.y_test is None or self.label_encoder is None:
            print("No test data or label encoder found. Train the model first.")
            return

        y_pred = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        print("Models Accuracy: {:.2f}%".format(accuracy * 100))

        print("Classification report:")
        print(classification_report(self.y_test, y_pred, target_names=self.label_encoder.classes_))

    def save(self) -> None:
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.feature_names, self.feature_path)

    def load_if_available(self, force_training: bool = False) -> tuple:
        if not force_training and os.path.exists(self.model_path) and os.path.exists(self.feature_path):
            return joblib.load(self.model_path), joblib.load(self.feature_path)
        return self.train()

    def train(self) -> tuple:
        df = self.training_data.copy()
        X = df.drop(columns=["outcome"])
        X = X.select_dtypes(include=["int64", "float64", "bool"])
        self.feature_names = X.columns.tolist()

        y = df["outcome"]
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        self.label_encoder = le

        X_train, self.X_test, y_train, self.y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )

        model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        model.fit(X_train, y_train)
        self.model = model
        self.debug()

        return model, self.feature_names

    def predict(self, p_data: dict) -> tuple:
        draft = pd.DataFrame([p_data])
        try:
            _draft = draft[self.feature_names]
        except KeyError as e:
            raise ValueError(f"Missing expected features in input: {e}")

        w_prob = self.model.predict_proba(_draft)
        predicted_outcome = self.model.predict(_draft)

        return w_prob[0][0], w_prob[0][1], predicted_outcome
