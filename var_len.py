import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import np_utils
from keras.preprocessing.sequence import pad_sequences
from keras.models import model_from_json
from keras.callbacks import ModelCheckpoint
import pickle
import requests

from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.grid_search import GridSearchCV


def get_all_cards(class_str):
    return requests.get('https://omgvamp-hearthstone-v1.p.mashape.com/cards/classes/' + class_str + '?collectible=1',
                        headers={
                            'X-Mashape-Key': 'NXohkzLH9CmshmkxPUTtI3d3k9ZNp1HIGwxjsnfBKub61oQpDR'
                        }).json()
    return cards

NEUTRAL = 'Neutral'
WARRIOR = 'Warrior'
SHAMAN = 'Shaman'
ROGUE = 'Rogue'
HUNTER = 'Hunter'
DRUID = 'Druid'
WARLOCK = 'Warlock'
MAGE = 'Mage'
PRIEST = 'Priest'
PALADIN = 'Paladin'

MAX_LEN = 30
MAX_INPUT_LEN = MAX_LEN - 1

with open('cards_by_class.pickle', 'rb') as handle:
    cards_by_class = pickle.load(handle)

with open('card_to_int.pickle', 'rb') as handle:
    card_to_int = pickle.load(handle)
with open('int_to_card.pickle', 'rb') as handle:
    int_to_card = pickle.load(handle)
with open('model.json', 'r') as handle:
    loaded_model_json = handle.read()
model = model_from_json(loaded_model_json)
model.load_weights("weightsrestrictions.final.h5")
# model.load_weights("weightsrestrictions.best.h5")


# model.load_weights("weights.final.h5")

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
                        words[-1] == 'TOG' or words[-1] == 'MSG'):
                card = ' '.join(words[0:-1])

            if (line[0] == '2'):
                cur_deck.append(card)
                cur_deck.append(card)
            else:
                cur_deck.append(card)
            unique_cards.add(card)


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
        # print("Deck is", deck_ints)
        for i in range(1000):
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

    def create_model():
        model = Sequential()
        model.add(Dense(8, input_dim=MAX_INPUT_LEN, activation='relu'))
        model.add(Dense(y.shape[1], activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    filepath = "weightsrestrictions.best.h5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    callbacks_list = [checkpoint]

    model = create_model()
    model.fit(X, y, nb_epoch=50, batch_size=100, verbose=1, validation_split=0.33, callbacks=callbacks_list)
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights("weightsrestrictions.final.h5")
    scores = model.evaluate(X, y, verbose=0)
    print("Model Accuracy: %.2f%%" % (scores[1] * 100))

    # model = KerasClassifier(build_fn=create_model)
    #
    # nb_epochs = [100, 125, 150]
    # batch_sizes = [1000]
    # param_grid = dict(nb_epoch=nb_epochs, batch_size=batch_sizes, verbose=[1], validation_split=[0.33])
    # grid = GridSearchCV(estimator=model, param_grid=param_grid)
    # grid_result = grid.fit(X, y)
    # print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    #
    # for params, mean_score, scores in grid_result.grid_scores_:
    #     print("%f (%f) with: %r" % (scores.mean(), scores.std(), params))

    cards_by_class = {}
    classes = [NEUTRAL, WARRIOR, SHAMAN, ROGUE, HUNTER, DRUID, WARLOCK, MAGE, PRIEST, PALADIN]
    for a_class in classes:
        cards_by_class[a_class] = {}
        cards_json = get_all_cards(a_class)
        for card_json in cards_json:
            cards_by_class[a_class][str(card_json['name'])] = str(card_json['rarity']) == 'Legendary'
    with open('cards_by_class.pickle', 'wb') as handle:
        pickle.dump(cards_by_class, handle)

    return model


def generate_deck(seed_cards, seed_class):
    str_class = str(seed_class)

    output = list(str(card) for card in seed_cards)

    seed_input = []
    for card in seed_cards:
        str_card = str(card)
        if str_card in card_to_int:
            seed_input.append(card_to_int[str_card])
            print("Using", str_card, "in seed")
        else:
            seed_input.append(0)
            print("Not using", str_card, "in seed")

    while len(seed_input) < 30:
        padded_input = pad_sequences([seed_input], maxlen=MAX_INPUT_LEN)
        padded_input = padded_input / float(len(card_to_int))
        prediction = model.predict(padded_input, verbose=0)
        # print("prediction", prediction.shape)
        sorted = numpy.argsort(prediction[0])

        for i in range(len(sorted) - 1, -1, -1):
            card_str = int_to_card[sorted[i]]
            if card_str in cards_by_class[str_class] or card_str in cards_by_class[NEUTRAL]:
                if card_str in cards_by_class[str_class]:
                    is_legendary = cards_by_class[str_class][card_str]
                else:
                    is_legendary = cards_by_class[NEUTRAL][card_str]
                occurrences = seed_input.count(sorted[i])
                if (is_legendary and occurrences < 1) or (not is_legendary and occurrences < 2):
                    seed_input.append(sorted[i])
                    break


    for i in range(len(seed_cards), 30):
        output.append(int_to_card[seed_input[i]])
    return output


if __name__ == "__main__":
    # test_input_text = ["Flame Imp", "SoulFire", "Voidwalker", "Dark Peddler", "Wrathguard", "Imp Gang Boss"]
    # test_input_text = ["Savage Roar", "Living Roots", "Swipe"]
    # test_input_text = ["Earthen Ring Farseer", "Nfsd", "Argent Squire", "Bloodmage Thalnos", "fsd"]
    # test_input_text = ["Mounted Raptor", "Mad Scientist", "Alexstrasza"]
    # test_input_text = ["Ice Barrier", "Frostbolt", "Archmage Antonidas", "Spider Tank GvG", "Loatheb", "Annoy-o-Tron GvG", "Cogmaster GvG"]
    # test_input_text = ["Northshire Cleric", "Twilight Guardian", "Sylvanas Windrunner", "Dr. Boom", "Wild Pyromancer"]
    # test_input_text = ["Cat Trick", "Unleash the Hounds", "Call of the Wild"]
    test_input_text = ["Kun the Forgotten King", "Aviana", "Feral Rage", "Call of the Wild", "call of the wild", "Wild Growth"]
    test_input_class = DRUID
    print(generate_deck(test_input_text, test_input_class))
    # model = train()
