.PHONY: flake8 test coverage style style_check

style:
	black --target-version=py36 dynamicsettings tests setup.py
	flake8 dynamicsettings tests

style_check:
	black --target-version=py36 --check dynamicsettings tests setup.py

flake8:
	flake8 dynamicsettings tests

test:
	tests/manage.py test $${TEST_ARGS:-tests}

coverage:
	PYTHONPATH="tests" \
		python -b -W always -m coverage run tests/manage.py test $${TEST_ARGS:-tests}
	coverage report
