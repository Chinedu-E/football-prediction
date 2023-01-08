from pipeline import utils as U
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from keras.layers import Dense, Dropout, Input
from keras.models import Model
from keras.optimizers import Adam

from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler


def build_model(input_shape):
    stat_inputs = Input(shape=input_shape)
    stats = Dense(42, activation="relu")(stat_inputs)
    stats = Dropout(0.5)(stats)
    stats = Dense(84, activation="relu")(stats)
    stats = Dropout(0.5)(stats)
    stats = Dense(42, activation="relu")(stats)
    x = Dense(3, activation="softmax")(stats)

    model = Model(inputs=stat_inputs, outputs=x)
    model.compile(
        loss="sparse_categorical_crossentropy",
        optimizer=Adam(1e-3),
        metrics=["accuracy"]
    )

    return model


def main():
    features = pd.read_csv("features.csv")
    num_teams = len(features["HomeTeam"].unique())
    labels = pd.read_csv("labels.csv")

    le = LabelEncoder()
    labels = le.fit_transform(labels)

    tokenizer = Tokenizer(num_words=num_teams)
    scaler = StandardScaler()

    teams, features = U.split_features(features)
    # team_sequences, tokenizer = U.teams_to_sequences(teams, tokenizer)
    features = scaler.fit_transform(features)

    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.05, random_state=0, shuffle=False)
    X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, test_size=0.0125, random_state=0, shuffle=False)

    print(f"shape of training data {X_train.shape}")
    print(f"shape of testing data {X_test.shape}")
    print(f"shape of validation data {X_val.shape}")

    rf = RandomForestClassifier(n_estimators=1000, n_jobs=-1)
    rf.fit(X_train, y_train)

    model = build_model((features.shape[1],))
    print(model.summary())

    hist = model.fit(X_train, y_train,
                     batch_size=10,
                     epochs=5,
                     validation_data=(X_test, y_test))

    tp = pd.read_csv("to_predict.csv")
    _, tp = U.split_features(tp)
    home = []
    away = []
    draw = []
    prob = model.predict(tp)
    for prob in prob:
        home.append(f'{prob[2]:.2f}')
        draw.append(f'{prob[1]:.2f}')
        away.append(f'{prob[0]:.2f}')

    model_predictions = pd.read_csv('fixtures.csv', encoding='cp1252')
    model_predictions = model_predictions[model_predictions['Div'] == 'E0'][['Date', 'Time', 'HomeTeam', 'AwayTeam']]
    model_predictions['1'] = home
    model_predictions['X'] = draw
    model_predictions['2'] = away

    model_predictions.to_csv(f'predictions.csv', index=False)


if __name__ == '__main__':
    main()
