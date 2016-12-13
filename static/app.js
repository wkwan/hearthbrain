var app = angular.module('app', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

app.controller('AppCtrl', function ($scope, $http) {
    // var url = 'http://localhost:5000';
    var url = '';

    $scope.seedCards = {};
    $scope.outputDeck = {};

    $scope.showSpinner = false;

    $scope.cardsByClass = {
        'Warrior': [],
        'Shaman': [],
        'Rogue': [],
        'Hunter': [],
        'Druid': [],
        'Warlock': [],
        'Mage': [],
        'Priest': []
    };

    $scope.neutralCards = [];

    $scope.selectedClass = 'Warrior';
    $scope.inputDeckClass = 'Warrior';

    $scope.selectedCard = null;

    $scope.changeClass = function () {
        if ($scope.cardsByClass[$scope.selectedClass].length == 0) {
            getClassCards();
        }

        if ($scope.neutralCards.length == 0) {
            getNeutralCards();
        }

        for (var card in $scope.seedCards) {
            if ($scope.neutralCards.indexOf(card) < 0) {
                delete $scope.seedCards[card];
            }
        }
    }

    function cardCount() {
        var cardCount = 0;
        for (var card in $scope.seedCards) {
            cardCount += $scope.seedCards[card];
        }
        return cardCount;
    }


    $scope.addCard = function () {
        if ($scope.selectedCard == null) return;
        if ($scope.selectedCard.name in $scope.seedCards) {
            if ($scope.seedCards[$scope.selectedCard.name] == 1) {
                if (cardCount() < 30 && $scope.selectedCard.rarity != "Legendary") $scope.seedCards[$scope.selectedCard.name] = 2;
            }
        } else {
            if (cardCount() < 30) $scope.seedCards[$scope.selectedCard.name] = 1;
        }
        delete $scope.selectedCard
    }

    $scope.removeCard = function (card) {
        if ($scope.seedCards[card] == 2) {
            $scope.seedCards[card] = 1;
        } else {
            delete $scope.seedCards[card];
        }
    }

    $scope.clear = function () {
        $scope.seedCards = {};
    }

    $scope.generateDeck = function () {
        $scope.showSpinner = true;
        var toSend = [];
        for (var card in $scope.seedCards) {
            toSend.push(card);
            if ($scope.seedCards[card] == 2) {
                toSend.push(card);
            }
        }
        $http.get(url + '/gen', {params: {seed: toSend, seed_class: $scope.selectedClass}}).success(function(generatedDeck) {
            $scope.outputDeck = {};
            for (var i in generatedDeck) {
                if (generatedDeck[i] in $scope.outputDeck) {
                    $scope.outputDeck[generatedDeck[i]] = 2;
                } else {
                    $scope.outputDeck[generatedDeck[i]] = 1;
                }
            }

            console.log($scope.outputDeck);

            $scope.showSpinner = false;
        });
    }

    getClassCards();
    getNeutralCards();

    function getClassCards() {
        $http({
            method: 'GET',
            url: 'https://omgvamp-hearthstone-v1.p.mashape.com/cards/classes/' + $scope.selectedClass + '?collectible=1',
            headers: {
                'X-Mashape-Key': 'NXohkzLH9CmshmkxPUTtI3d3k9ZNp1HIGwxjsnfBKub61oQpDR'
            }
        }).then(function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            if (response.status == 200) {
                for (var i = 0; i < response.data.length; i++) {
                    var card = response.data[i];
                    if (card.type == "Minion" || card.type == "Spell" || card.type == "Weapon" && card.collectible) {
                        $scope.cardsByClass[$scope.selectedClass].push(card);
                    }
                }

            }
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
        });
    }

    function getNeutralCards() {
        $http({
            method: 'GET',
            url: 'https://omgvamp-hearthstone-v1.p.mashape.com/cards/classes/Neutral?collectible=1',
            headers: {
                'X-Mashape-Key': 'NXohkzLH9CmshmkxPUTtI3d3k9ZNp1HIGwxjsnfBKub61oQpDR'
            }
        }).then(function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            if (response.status == 200) {
                for (var i = 0; i < response.data.length; i++) {
                    var card = response.data[i];
                    if (card.type == "Minion" || card.type == "Spell" || card.type == "Weapon" && card.collectible) {
                        $scope.neutralCards.push(card);
                    }

                }

            }
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
        });
    }
})
