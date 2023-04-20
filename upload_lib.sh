python setup.py sdist bdist_wheel
twine check dist/*

twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*
# twine upload --skip-existing dist/*