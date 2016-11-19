import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import np_utils
from keras.preprocessing.sequence import pad_sequences
from keras.models import model_from_json
from keras.callbacks import ModelCheckpoint

def generateDeck():
    # fix random seed for reproducibility
    numpy.random.seed(7)

    MAX_LEN = 30
    MAX_INPUT_LEN = MAX_LEN - 1

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
            if (line[0] == '2'):
                cur_deck.append(card)
                cur_deck.append(card)
            else:
                cur_deck.append(card)
            unique_cards.add(card)

    print(len(unique_cards))

    card_to_int = dict((c, i + 1) for i, c in enumerate(unique_cards))
    int_to_card = dict((i + 1, c) for i, c in enumerate(unique_cards))


    def train():
        dataX = []
        dataY = []

        for deck in decks:
            deck_ints = list(card_to_int[card] for index, card in enumerate(deck))
            print("Deck is", deck_ints)
            for i in range(300):
                input_len = numpy.random.randint(2, MAX_LEN)
                input = numpy.random.choice(deck_ints, input_len)
                dataX.append(input[:len(input)-1])
                dataY.append(input[len(input)-1])
                # print(dataX[len(dataX)-1], '->', dataY[len(dataY)-1])

        print("before padding")
        X = pad_sequences(dataX, maxlen=MAX_INPUT_LEN, dtype='float32')
        print("first padded", X[0]);
        print("first padded", X[1]);
        print("first padded", X[2]);
        print("first padded", X[3]);

        # normalize
        X = X / float(len(unique_cards))
        # one hot encode the output variable
        y = np_utils.to_categorical(dataY)
        print("shapes", X.shape, y.shape)

        batch_size=1

        model = Sequential()
        model.add(Dense(8, input_dim=MAX_INPUT_LEN, activation='relu'))
        model.add(Dense(y.shape[1], activation='softmax'))

        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        filepath="weights.best.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
        callbacks_list = [checkpoint]

        model.fit(X, y, nb_epoch=20, batch_size=batch_size, verbose=2, validation_split=0.33, callbacks=callbacks_list)

        model_json = model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
        model.save_weights("weights.final.h5")

        scores = model.evaluate(X, y, verbose=0)
        print("Model Accuracy: %.2f%%" % (scores[1]*100))

        return model

    def generate(model):
        test_input_text = ["Mounted Raptor LoE", "Savage Roar", "Living Roots TGT", "Swipe", "Big Game Hunter"]
        # test_input_text = ["Earthen Ring Farseer", "Argent Squire", "Bloodmage Thalnos"]
        # test_input_text = ["Mounted Raptor LoE", "Mad Scientist Naxx", "Alexstrasza"]
        # test_input_text = ["Ice Barrier", "Frostbolt", "Archmage Antonidas", "Spider Tank GvG", "Loatheb Naxx", "Annoy-o-Tron GvG", "Cogmaster GvG"]
        # test_input_text = ["Northshire Cleric", "Twilight Guardian TGT"]
        test_input = list(card_to_int[card] for card in test_input_text)
        generated_deck_len = len(test_input)
        while len(test_input) < 30:
            padded_input = pad_sequences([test_input], maxlen=MAX_INPUT_LEN)
            print("padded input is", padded_input)
            padded_input = padded_input / float(len(unique_cards))
            prediction = model.predict(padded_input, verbose=0)
            index = numpy.argmax(prediction)
            result = int_to_card[index]
            print("generated", result)
            test_input.append(index)

        return list(int_to_card[card_int] for card_int in test_input)

    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # model.load_weights("weights.final.h5")
    model.load_weights("weights.best.hdf5")

    # model = train()
    return generate(model)