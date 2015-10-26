// https://www.npmjs.com/
var gulp = require('gulp');
var sass = require('gulp-sass');
var plumber = require('gulp-plumber');
var watch = require('gulp-watch');
var prefix = require('gulp-autoprefixer');
var minifycss = require('gulp-minify-css');

gulp.task('sass', function () {
  gulp.src('bower_components/foundation/scss/**.scss')
  .pipe(plumber())
  .pipe(sass({errLogToConsole: true, includePaths: ['bower_components/foundation/scss']}))
  .pipe(prefix(
                "last 3 version", "> 1%", "ie 8", "ie 7"
                ))
  /*.pipe(gulp.dest('static/css'))
  .pipe(minifycss())*/
  .pipe(gulp.dest('static/css'));
});

gulp.task('default', function() {
  gulp.run( 'sass');
  gulp.watch('static/scss/**', function(event) {
  gulp.run('sass');
  })
});