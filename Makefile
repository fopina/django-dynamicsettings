.PHONY: test coverage style style_check

style:
	black --target-version=py36 \
	      --line-length=120 \
		  --skip-string-normalization \
		  dynamicsettings tests setup.py

style_check:
	black --target-version=py36 \
	      --line-length=120 \
		  --skip-string-normalization \
		  --check \
		  dynamicsettings tests setup.py

test:
	tests/manage.py test $${TEST_ARGS:-tests}

coverage:
	PYTHONPATH="tests" \
		python -b -W always -m coverage run tests/manage.py test $${TEST_ARGS:-tests}
	coverage report
