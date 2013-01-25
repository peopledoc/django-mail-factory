flake8:
	flake8 mail_factory --ignore=E501,E127,E128,E124

test:
	coverage run --branch --source=mail_factory demo/manage.py test mail_factory
	coverage report --omit=mail_factory/test*
