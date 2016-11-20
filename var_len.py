import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import np_utils
from keras.preprocessing.sequence import pad_sequences
from keras.models import model_from_json
from keras.callbacks import ModelCheckpoint
import pickle

MAX_LEN = 30
MAX_INPUT_LEN = MAX_LEN - 1
with open('card_to_int.pickle', 'rb') as handle:
    card_to_int = pickle.load(open('card_to_int.pickle', 'rb'))
with open('int_to_card.pickle', 'rb') as handle:
    int_to_card = pickle.load(open('int_to_card.pickle', 'rb'))
with open('model.json', 'r') as handle:
    loaded_model_json = handle.read()
model = model_from_json(loaded_model_json)
# model.load_weights("weights.final.h5")
model.load_weights("weights.final.h5")

def train():
    numpy.random.seed(7)

    lines = open('decks.txt').readlines()

    decks = []

    unique_cards = set()

    cur_deck = []
    for line in lines:
        if not line.strip():
            decks.append(cur_deck)
            cur_deck = []
        else:
            card = line[3:].strip()

            words = card.split()
            if (words[-1] == 'LoE' or words[-1] == 'Kara' or words[-1] == 'Naxx' or
                        words[-1] == 'GvG' or words[-1] == 'BrM' or words[-1] == 'TGT' or
                        words[-1] == 'TOG'):
                card = ' '.join(words[0:-1])

            if (line[0] == '2'):
                cur_deck.append(card)
                cur_deck.append(card)
            else:
                cur_deck.append(card)
            unique_cards.add(card)

    print(len(unique_cards))

    card_to_int = dict((c, i + 1) for i, c in enumerate(unique_cards))
    int_to_card = dict((i + 1, c) for i, c in enumerate(unique_cards))

    with open('card_to_int.pickle', 'wb') as handle:
        pickle.dump(card_to_int, handle)

    with open('int_to_card.pickle', 'wb') as handle:
        pickle.dump(int_to_card, handle)
    dataX = []
    dataY = []

    for deck in decks:
        deck_ints = list(card_to_int[card] for index, card in enumerate(deck))
        print("Deck is", deck_ints)
        for i in range(10000):
            input_len = numpy.random.randint(2, MAX_LEN)
            input = numpy.random.choice(deck_ints, input_len)
            dataX.append(input[:len(input) - 1])
            dataY.append(input[len(input) - 1])
            # print(dataX[len(dataX)-1], '->', dataY[len(dataY)-1])

    X = pad_sequences(dataX, maxlen=MAX_INPUT_LEN, dtype='float32')
    # normalize
    X = X / float(len(card_to_int))
    # one hot encode the output variable
    y = np_utils.to_categorical(dataY)
    print("shapes", X.shape, y.shape)

    batch_size = 1

    model = Sequential()
    model.add(Dense(8, input_dim=MAX_INPUT_LEN, activation='relu'))
    model.add(Dense(y.shape[1], activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    filepath = "weights.best.h5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    callbacks_list = [checkpoint]

    model.fit(X, y, nb_epoch=3, batch_size=batch_size, verbose=2, validation_split=0.33, callbacks=callbacks_list)

    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights("weights.final.h5")

    scores = model.evaluate(X, y, verbose=0)
    print("Model Accuracy: %.2f%%" % (scores[1] * 100))

    return model


def generate_deck(seed_cards):
    seed_input = []
    for card in seed_cards:
        str_card = str(card)
        if str_card in card_to_int:
            seed_input.append(card_to_int[str_card])

    print("going to use seed input of", seed_input)

    while len(seed_input) < 30:
        padded_input = pad_sequences([seed_input], maxlen=MAX_INPUT_LEN)
        padded_input = padded_input / float(len(card_to_int))
        prediction = model.predict(padded_input, verbose=0)
        index = numpy.argmax(prediction)
        seed_input.append(index)

    return list(int_to_card[card_int] for card_int in seed_input)


if __name__ == "__main__":
    # test_input_text = ["Savage Roar", "Living Roots", "Swipe"]
    # test_input_text = ["Earthen Ring Farseer", "Argent Squire", "Bloodmage Thalnos"]
    # test_input_text = ["Mounted Raptor LoE", "Mad Scientist Naxx", "Alexstrasza"]
    # test_input_text = ["Ice Barrier", "Frostbolt", "Archmage Antonidas", "Spider Tank GvG", "Loatheb Naxx", "Annoy-o-Tron GvG", "Cogmaster GvG"]
    # test_input_text = ["Northshire Cleric", "Twilight Guardian TGT", "Sylvanas Windrunner", "Dr. Boom", "Wild Pyromancer"]
    test_input_text = ["Cat Trick", "Unleash the Hounds", "Call of the Wild"]
    print(generate_deck(test_input_text))
    # model = train()
