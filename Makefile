flake8:
	flake8 mail_factory

test:
	coverage run --branch --source=mail_factory demo/manage.py test mail_factory
	coverage report --omit=mail_factory/test*
