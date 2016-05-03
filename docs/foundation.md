# Foundation

Swiftbrowser uses [Zurb Foundation](http://foundation.zurb.com/sites/docs/) as an alternative to Twitter Bootstrap. Foundation is an instance of a [Compass](http://compass-style.org/) project. Compass projects come with a convenient tool that compiles [Sass](http://sass-lang.com/) and concatenates it into one file.

## Requirements

* Ruby version 2.0 or greater

## Getting started
1. Install compass.
	```bash
	sudo gem install compass -v 1.0.3
	```

2. Install foundation. Currently we are using Foundation 5. Foundation 6 is available but we haven't had time to upgrade to it yet. As you can see, the instructions below specifies installing foundation 1.0.4. This refers to the Foundation CLI. Version 1.0.4 of the Foundation CLI 1.0.4 is linked to Foundation 5.

	```bash
	sudo gem install foundation -v 1.0.4
	```

3. From the django-swiftbrowser repository root, change into the compass project directory.

	```bash
	cd swiftbrowser/static/foundation
	```

4. Run compass.
	```bash
	compass watch
	```

Now anytime you save files within swiftbrowser/static/foundation/scss/, compass will compile it into swiftbrowser/static/foundation/stylesheets/app.css which is used on every page in Swiftbrowser.
