/**
 * Date: 01/05/16
 * Author: Shirish Goyal
 */

module.exports = function (grunt) {

    var appConfig = grunt.file.readJSON('package.json');

    // Load grunt tasks automatically
    // see: https://github.com/sindresorhus/load-grunt-tasks
    require('load-grunt-tasks')(grunt);

    var pathsConfig = function (appName) {
        this.app = appName || appConfig.name;

        return {
            app: this.app,
            templates: 'static/templates',
            sass: 'static/css',
            fonts: 'static/fonts',
            images: 'static/images',
            js: 'static/js',
            port: '8000'
        }
    };

    grunt.initConfig({

        paths: pathsConfig(),
        pkg: appConfig,

        // see: https://github.com/gruntjs/grunt-contrib-watch
        watch: {
            gruntfile: {
                files: ['Gruntfile.js']
            },
            sass: {
                files: ['<%= paths.sass %>/**/*.{scss,sass}'],
                tasks: ['sass:dev'],
                options: {
                    atBegin: true,
                    debounceDelay: 5000,
                }
            },
            livereload: {
                files: [
                    '<%= paths.js %>/**/*.js',
                    '<%= paths.sass %>/**/*.{scss,sass}',
                    '<%= paths.templates %>/**/*.html'
                ],
                options: {
                    spawn: false,
                    livereload: true
                }
            },
            flake8: {
                files: [
                    'csp/*.py',
                    'crowdsourcing/middleware/*.py',
                    'crowdsourcing/permissions/*.py',
                    'crowdsourcing/serializers/*.py',
                    'crowdsourcing/validators/*.py',
                    'crowdsourcing/viewsets/*.py',
                    'crowdsourcing/*.py'
                ],
                tasks: ['flake8'],
                options: {
                    atBegin: true
                }
            }
        },

        flake8: {
            options: {
                errorsOnly: true,
                maxComplexity: 12,
                maxLineLength: 119,
                ignore: ['E123', 'E128', 'E133', 'E402', 'W503', 'E731', 'W601', 'F403'],
                hangClosing: true,
                showPep8: true
            },
            src: [
                'csp/*.py',
                'crowdsourcing/middleware/*.py',
                'crowdsourcing/permissions/*.py',
                'crowdsourcing/serializers/*.py',
                'crowdsourcing/validators/*.py',
                'crowdsourcing/viewsets/*.py',
                'crowdsourcing/*.py',
                'mturk/*.py'
            ]
        },

        // see: https://github.com/sindresorhus/grunt-sass
        sass: {
            dev: {
                options: {
                    outputStyle: 'compressed',
                    sourceMap: true,
                    precision: 10
                },
                files: {
                    '<%= paths.sass %>/app.css': '<%= paths.sass %>/app.scss'
                }
            },
            dist: {
                options: {
                    outputStyle: 'compressed',
                    sourceMap: true,
                    precision: 10
                },
                files: {
                    '<%= paths.sass %>/app.css': '<%= paths.sass %>/app.scss'
                }
            }
        },

        //see https://github.com/nDmitry/grunt-postcss
        postcss: {
            options: {
                map: true, // inline sourcemaps

                processors: [
                    require('pixrem')(), // add fallbacks for rem units
                    require('autoprefixer-core')({
                        browsers: [
                            'Android 2.3',
                            'Android >= 4',
                            'Chrome >= 20',
                            'Firefox >= 24',
                            'Explorer >= 8',
                            'iOS >= 6',
                            'Opera >= 12',
                            'Safari >= 6'
                        ]
                    }), // add vendor prefixes
                    require('cssnano')() // minify the result
                ]
            },
            dist: {
                src: '<%= paths.sass %>/app.css'
            }
        },

        // see: https://npmjs.org/package/grunt-bg-shell
        bgShell: {
            _defaults: {
                bg: true
            },
            run: {
                cmd: 'uwsgi uwsgi-dev.ini'
            }
        }
    });

    grunt.registerTask('serve', [
        'bgShell:run',
        'watch'
    ]);

    grunt.registerTask('build', [
        'sass:dist',
        'postcss'
    ]);

    grunt.registerTask('default', [
        'build'
    ]);
};

