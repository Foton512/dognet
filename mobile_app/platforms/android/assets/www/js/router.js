(function () {
    'use strict';

    angular.module('app')
        .config(['$stateProvider', '$urlRouterProvider', '$compileProvider', setupRouter]);

    function setupRouter($stateProvider, $urlRouterProvider, $compileProvider) {
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|file|ghttps?|ms-appx|x-wmapp0)|\/?app\//);

        $stateProvider
            .state('app', {
                url: '/app',
                abstract: true,
                templateUrl: 'views/master.html'
            })
			.state('app.home', {
                url: '/home',
                views: {
                    'nestedHolder': {
                        templateUrl: 'views/home.html',
						controller: 'HomeCtrl as vm'
                    }					
                }
            })
            .state('app.auth', {
                url: '/map',
                views: {
                    'nestedHolder': {
                        templateUrl: 'views/auth.html',
                        controller: 'AuthCtrl as vm'
                    }
                }
            })
            .state('app.dog', {
                url: '/dog/:id',
                views: {
                    'nestedHolder': {
                        resolve: {
                            dog: function ($stateParams, DogService) {
                                return DogService.getById($stateParams.id);
                            }
                        },
                        templateUrl: 'views/dog.html',
                        controller: 'DogCtrl as vm'
                    }
                }
            })
            .state('app.relations', {
                    url: '/relations/:id',
                    views: {
                        'nestedHolder': {
                            resolve: {
                                dog: function ($stateParams, DogService) {
                                    return DogService.getById($stateParams.id);
                                }
                            },
                            templateUrl: 'views/relations.html',
                            controller: 'RelationsCtrl as vm'
                        }
                    }
                });

		$urlRouterProvider.otherwise('/app/home');
	}
})();