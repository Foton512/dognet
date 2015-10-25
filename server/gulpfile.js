// Объявляем наши плагины
var gulp = require('gulp');
var sass = require('gulp-sass');
var plumber = require('gulp-plumber');
var watch = require('gulp-watch');

gulp.task('sass', function () {
  gulp.src('static/scss/**.scss')
  .pipe(plumber())
  .pipe(sass({errLogToConsole: true}))
  .pipe(gulp.dest('static/css'));
});

gulp.task('default', function() {
  gulp.run( 'sass');
  gulp.watch('static/scss/**', function(event) {
  gulp.run('sass');
  })
});