(function () {
    'use strict';

    angular
        .module('crowdsource.routes', ['ui.router'])
        .config(config);

    config.$inject = ['$stateProvider', '$urlRouterProvider'];

    /**
     * @name config
     * @desc Define valid application routes
     */
    function config($stateProvider, $urlRouterProvider) {

        // Views
        var login = {
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/login.html'
        };

        var logout = {
            controller: 'LogoutController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/login.html'
        };

        var register = {
            controller: 'RegisterController',
            controllerAs: 'register',
            templateUrl: '/static/templates/authentication/register.html'
        };

        var forgotPassword = {
            controller: 'AuthSettingsController',
            controllerAs: 'auth',
            templateUrl: '/static/templates/authentication/forgot-password.html'
        };

        var resetPassword = {
            controller: 'AuthSettingsController',
            controllerAs: 'auth',
            templateUrl: '/static/templates/authentication/reset-password.html'
        };

        var changePassword = {
            controller: 'AuthSettingsController',
            controllerAs: 'auth',
            templateUrl: '/static/templates/authentication/change-password.html'
        };

        var activateAccount = {
            controller: 'AuthSettingsController',
            controllerAs: 'auth',
            templateUrl: '/static/templates/authentication/activate-account.html'
        };

        var unsubscribe = {
            controller: 'PreferencesController',
            controllerAs: 'preferences',
            templateUrl: '/static/templates/user/unsubscribe.html'
        };

        var irb = {
            templateUrl: '/static/templates/user/irb.html'
        };

        var home = {
            templateUrl: '/static/templates/layout/home.html',
            controller: 'HomeController',
            controllerAs: 'vm'
        };

        var demo = {
            templateUrl: '/static/templates/layout/demo.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var phd_demo = {
            templateUrl: '/static/templates/demo/cs-phd.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var trump_afterdark_demo = {
            templateUrl: '/static/templates/demo/trumpafterdark.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var reviseandresubmit_demo = {
            templateUrl: '/static/templates/demo/reviseandresubmit.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var gradschool_demo = {
            templateUrl: '/static/templates/demo/gradschoolfriends.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var botcheck_demo = {
            templateUrl: '/static/templates/demo/botcheck.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var reddit_demo = {
            templateUrl: '/static/templates/demo/reddit.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var webpage_demo = {
            templateUrl: '/static/templates/demo/webpage.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var difference_demo = {
            templateUrl: '/static/templates/demo/difference.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var images_demo = {
            templateUrl: '/static/templates/demo/images.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var marijuana_demo = {
            templateUrl: '/static/templates/demo/marijuana.html',
            controller: 'DemoController',
            controllerAs: 'vm'
        };

        var auth = {
            templateUrl: '/static/templates/layout/auth.html',
            controller: 'HomeController',
            controllerAs: 'vm'
        };

        var navbar = {
            templateUrl: '/static/templates/layout/navbar.html',
            controller: 'NavbarController',
            controllerAs: 'vm'
        };

        var profile = {
            templateUrl: '/static/templates/user/profile.html',
            controller: 'UserController',
            controllerAs: 'vm'
        };

        var publicProfile = {
            templateUrl: '/static/templates/user/public-profile.html',
            controller: 'PublicProfileController',
            controllerAs: 'profile'
        };

        var bonus = {
            templateUrl: '/static/templates/payment/bonus.html',
            controller: 'BonusController',
            controllerAs: 'bonus'
        };

        var getting_started = {
            templateUrl: '/static/templates/user/getting-started.html',
            controller: 'UserController',
            controllerAs: 'user'
        };

        var requesterProfile = {
            templateUrl: '/static/templates/requester/home.html',
            controller: 'RequesterProfileController'
        };

        var paymentCreditCard = {
            controller: 'PaymentController',
            controllerAs: 'payment',
            templateUrl: '/static/templates/payment/credit-card.html'
        };
        var paymentBank = {
            controller: 'PaymentController',
            controllerAs: 'payment',
            templateUrl: '/static/templates/payment/bank.html'
        };
        var paymentDeposit = {
            controller: 'PaymentController',
            controllerAs: 'payment',
            templateUrl: '/static/templates/payment/deposit.html'
        };

        var dashboard = {
            templateUrl: '/static/templates/dashboard/dashboard.html',
            controller: 'DashboardController',
            controllerAs: 'dashboard'
        };

        var createProject = {
            controller: 'ProjectController',
            controllerAs: 'project',
            templateUrl: '/static/templates/project/authoring.html'
        };

        var myProjects = {
            controller: 'MyProjectController',
            controllerAs: 'project',
            templateUrl: '/static/templates/project/project-list.html'
        };


        var projectReview = {
            controller: 'ProjectReviewController',
            controllerAs: 'review',
            templateUrl: '/static/templates/project/submission-review-tabular.html'
        };

        var taskReview = {
            controller: 'TaskReviewController',
            controllerAs: 'preview',
            templateUrl: '/static/templates/task/preview.html'
        };

        var myTasks = {
            templateUrl: '/static/templates/project/my-tasks.html',
            controller: 'MyTasksController',
            controllerAs: 'myTasks'
        };

        var messages = {
            templateUrl: '/static/templates/message/inbox.html',
            controller: 'MessageController',
            controllerAs: 'inbox'
        };

        var overlay = {
            templateUrl: '/static/templates/message/overlay.html',
            controller: 'OverlayController',
            controllerAs: 'overlay'
        };

        var taskFeed = {
            templateUrl: '/static/templates/task-feed/main.html',
            controller: 'TaskFeedController',
            controllerAs: 'taskfeed'
        };

        var projectPreview = {
            templateUrl: '/static/templates/project/preview.html',
            controller: 'TaskFeedController',
            controllerAs: 'taskfeed'
        };

        var root = {
            template: '<div></div>',
            controller: 'HomeRoutingController',
            controllerAs: 'root'
        };

        var task = {
            templateUrl: '/static/templates/task/base.html',
            controller: 'TaskController',
            controllerAs: 'task'
        };

        var preferences = {
            templateUrl: '/static/templates/project/preferences.html',
            controller: 'PreferencesController',
            controllerAs: 'preferences'
        };

        var docsGettingStarted = {
            controller: 'DocsController',
            controllerAs: 'docs',
            templateUrl: '/static/templates/docs/getting-started.html'
        };

        var docsProjects = {
            controller: 'DocsController',
            controllerAs: 'docs',
            templateUrl: '/static/templates/docs/projects.html'
        };

        var docsTasks = {
            controller: 'DocsController',
            controllerAs: 'docs',
            templateUrl: '/static/templates/docs/tasks.html'
        };
        var docsAssignments = {
            controller: 'DocsController',
            controllerAs: 'docs',
            templateUrl: '/static/templates/docs/assignments.html'
        };
        var docsTemplates = {
            controller: 'DocsController',
            controllerAs: 'docs',
            templateUrl: '/static/templates/docs/templates.html'
        };

        var docsTemplateItems = {
            controller: 'DocsController',
            controllerAs: 'docs',
            templateUrl: '/static/templates/docs/template-items.html'
        };

        var docsOAuth2 = {
            controller: 'DocsController',
            controllerAs: 'docs',
            templateUrl: '/static/templates/docs/oauth2.html'
        };

        var docs = {
            templateUrl: '/static/templates/layout/docs.html',
            controller: 'DemoController',
            controllerAs: 'docsParent'
        };
        // States
        $stateProvider

            .state('home', {
                url: '/home',
                views: {
                    'fullscreen': home
                },
                authenticate: false
            })
            .state('demo', {
                url: '/demo',
                abstract: true,
                views: {
                    'fullscreen': demo
                },
                authenticate: false
            })
            .state('demo.reddit', {
                url: '/reddit',
                views: {
                    'content': reddit_demo
                },
                authenticate: false
            })
            .state('demo.phd', {
                url: '/cs-phd',
                title: 'Where will you land after attending a top CS grad school?',
                views: {
                    'content': phd_demo
                },
                authenticate: false
            })
            .state('demo.trumpafterdark', {
                url: '/trump-afterdark',
                title: 'Trump After Dark: algorithmically augmented funny',
                views: {
                    'content': trump_afterdark_demo
                },
                authenticate: false
            })
            .state('demo.reviseandresubmit', {
                url: '/reviseandresubmit',
                title: 'Revise and Resubmit: why one crowd worker beats one million',
                views: {
                    'content': reviseandresubmit_demo
                },
                authenticate: false
            })
            .state('demo.gradschoolfriends', {
                url: '/gradschoolfriends',
                title: 'Who did your advisor know in grad school?',
                views: {
                    'content': gradschool_demo
                },
                authenticate: false
            })
            .state('demo.botcheck', {
                url: '/botcheck',
                title: 'Identifying Harassment Bots on Twitter',
                views: {
                    'content': botcheck_demo
                },
                authenticate: false
            })
            .state('demo.webpage', {
                url: '/webpage',
                views: {
                    'content': webpage_demo
                },
                authenticate: false
            })
            .state('demo.difference', {
                url: '/difference',
                views: {
                    'content': difference_demo
                },
                authenticate: false
            })
            .state('demo.images', {
                url: '/images',
                views: {
                    'content': images_demo
                },
                authenticate: false
            })
            .state('demo.marijuana', {
                url: '/marijuana',
                views: {
                    'content': marijuana_demo
                },
                authenticate: false
            })


            .state('docs', {
                url: '/docs',
                abstract: true,
                views: {
                    'fullscreen': docs
                },
                authenticate: false
            })
            .state('docs.getting_started', {
                url: '/getting-started',
                views: {
                    'content': docsGettingStarted
                },
                authenticate: false
            })

            .state('docs.projects', {
                url: '/projects',
                views: {
                    'content': docsProjects
                },
                authenticate: false
            })
            .state('docs.tasks', {
                url: '/tasks',
                views: {
                    'content': docsTasks
                },
                authenticate: false
            })

            .state('docs.assignments', {
                url: '/assignments',
                views: {
                    'content': docsAssignments
                },
                authenticate: false
            })
            .state('docs.templates', {
                url: '/templates',
                views: {
                    'content': docsTemplates
                },
                authenticate: false
            })
            .state('docs.template_items', {
                url: '/template-items',
                views: {
                    'content': docsTemplateItems
                },
                authenticate: false
            })
            .state('docs.oauth2', {
                url: '/oauth2-authentication',
                views: {
                    'content': docsOAuth2
                },
                authenticate: false
            })
            .state('auth', {
                url: '/auth',
                abstract: true,
                views: {
                    'fullscreen': auth
                },
                authenticate: false
            })
            .state('auth.login', {
                url: '/login?:next',
                views: {
                    'content': login
                },
                authenticate: false
            })
            .state('auth.logout', {
                url: '/logout',
                views: {
                    'content': logout
                },
                authenticate: false
            })
            .state('auth.irb', {
                url: '/irb',
                views: {
                    'content': irb
                },
                authenticate: false
            })
            .state('auth.register', {
                url: '/register',
                views: {
                    'content': register
                },
                authenticate: false
            })

            .state('change_password', {
                url: '/change-password',
                views: {
                    'navbar': navbar,
                    'content': changePassword
                },
                authenticate: false
            })

            .state('auth.forgot_password', {
                url: '/forgot-password',
                views: {
                    'content': forgotPassword
                },
                authenticate: false
            })

            .state('activate_account', {
                url: '/account-activation/:activation_key',
                views: {
                    'content': activateAccount
                },
                authenticate: false
            })
            .state('unsubscribe', {
                url: '/unsubscribe',
                views: {
                    'navbar': navbar,
                    'content': unsubscribe
                },
                authenticate: true
            })

            .state('reset_password', {
                url: '/reset-password/:reset_key/:enable',
                views: {
                    'content': resetPassword
                },
                authenticate: false
            })

            .state('dashboard', {
                url: '/dashboard',
                views: {
                    'navbar': navbar,
                    'content': dashboard,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('profile', {
                url: '/profile',
                title: 'Settings',
                views: {
                    'navbar': navbar,
                    'content': profile,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('public_profile', {
                url: '/u/:handle',
                views: {
                    'navbar': navbar,
                    'content': publicProfile,
                    'chat': overlay
                },
                authenticate: true
            })
            .state('bonus', {
                url: '/bonus/:handle',
                views: {
                    'navbar': navbar,
                    'content': bonus,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('getting_started', {
                url: '/getting-started',
                views: {
                    'navbar': navbar,
                    'content': getting_started
                },
                authenticate: true
            })


            .state('payment_deposit', {
                url: '/payment-deposit?:suggestedAmount?:redirectTo',
                title: 'Deposit',
                views: {
                    'navbar': navbar,
                    'content': paymentDeposit,
                    'chat': overlay
                },
                authenticate: true
            })
            .state('payment_card', {
                url: '/payment-card',
                title: 'Edit Credit Card',
                views: {
                    'navbar': navbar,
                    'content': paymentCreditCard,
                    'chat': overlay
                },
                authenticate: true
            })
            .state('payment_bank', {
                url: '/payment-bank',
                title: 'Edit Bank Information',
                views: {
                    'navbar': navbar,
                    'content': paymentBank,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('my_tasks', {
                url: '/my-tasks',
                title: 'Worker',
                views: {
                    'navbar': navbar,
                    'content': myTasks,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('create_edit_project', {
                url: '/project/:projectId',
                views: {
                    'navbar': navbar,
                    'content': createProject,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('my_projects', {
                url: '/my-projects',
                title: 'Requester',
                views: {
                    'navbar': navbar,
                    'content': myProjects,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('project_review', {
                url: '/project-review/:projectId',
                views: {
                    'navbar': navbar,
                    'content': projectReview,
                    'chat': overlay
                },
                authenticate: true,
                resolve: {
                    resolvedData: function ($stateParams, Project) {
                        return Project.retrieve($stateParams.projectId);
                    }
                }
            })

            /*.state('project_review', {
             url: '/project-review/:projectId',
             views: {
             'navbar': navbar,
             'content': projectReview,
             'chat': overlay
             },
             authenticate: true,
             resolve: {
             resolvedData: function ($stateParams, Project) {
             return Project.retrieve($stateParams.projectId);
             }
             }
             })*/

            .state('messages', {
                url: '/messages/?t',
                views: {
                    'navbar': navbar,
                    'content': messages
                },
                authenticate: true
            })

            .state('task', {
                url: '/task/:taskId/:returned?',
                views: {
                    'navbar': navbar,
                    'content': task,
                    'chat': overlay
                },
                authenticate: true
            })
            .state('task_review', {
                url: '/task-preview/:taskWorkerId',
                views: {
                    'navbar': navbar,
                    'content': taskReview,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('task_project', {
                url: '/task-feed/:projectId?',
                title: 'Project Preview',
                views: {
                    'navbar': navbar,
                    'content': projectPreview,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('task_feed', {
                url: '/task-feed',
                title: 'Task Feed',
                views: {
                    'navbar': navbar,
                    'content': taskFeed,
                    'chat': overlay
                },
                authenticate: true
            })
            .state('requester_settings', {
                url: '/requester-settings',
                title: 'Requester Settings',
                views: {
                    'navbar': navbar,
                    'content': preferences,
                    'chat': overlay
                },
                authenticate: true
            })

            .state('root', {
                url: '/',
                views: {
                    // 'navbar': navbar,
                    'content': root
                    // 'chat': overlay
                },
                authenticate: false
            })
            .state('empty', {
                url: '',
                views: {
                    // 'navbar': navbar,
                    'content': root
                    // 'chat': overlay
                },
                authenticate: false
            })

            .state('home-old', {
                url: '/home-old',
                views: {
                    'fullscreen': home
                },
                authenticate: false
            })
        ;


        $urlRouterProvider.otherwise("/home");
    }
})();
