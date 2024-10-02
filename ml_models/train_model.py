# ml_models/train_model.py
# type: ignore
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

def train_model():
    # Load features
    features = pd.read_csv('features.csv')

    # Simulate labels (in real scenarios, you'd have actual labels)
    # For this example, let's mark transactions over $8000 or with high risk features as fraud
    conditions = (features['amount'] > 8000) | (features['is_foreign'] == 1) | (features['ip_risk'] == 1)
    features['label'] = conditions.astype(int)

    X = features.drop(['transaction_id', 'label'], axis=1)
    y = features['label']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    score = model.score(X_test, y_test)
    print(f"Model accuracy: {score * 100:.2f}%")

    # Save the model
    joblib.dump(model, 'model.pkl')
    print("Model saved to model.pkl")

if __name__ == '__main__':
    train_model()
