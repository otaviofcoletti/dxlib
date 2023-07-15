#!/bin/bash

# Function to display script usage
display_usage() {
    echo "Usage: $0 [version] [tag]"
    echo "  version: Specify the version of the library. If not provided, it will default to '0.1.0'."
    echo "  tag: Specify the tag to determine the repository ('test' for test.pypi.org, 'prod' for pypi.org). If not provided, it will default to 'test'."
}

# Get the version and tag arguments from the command line
version="${1:-0.1.0}"
tag="${2:-test}"

# Display script usage if '-h' or '--help' option is provided
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    display_usage
    exit 0
fi

echo "Building the distribution package..."
export DXLIB_VERSION="$version"
python setup.py sdist bdist_wheel
unset DXLIB_VERSION

# Verify the distribution package using twine check
echo "Verifying the distribution package..."
twine check dist/*


# Run the upload command based on the tag
if [[ "$tag" == "test" ]]; then
    echo "Uploading to the test PyPI server..."
    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*$version*
    rm -rf dist/*.tar.gz
    rm -rf dist/*.whl
elif [[ "$tag" == "prod" ]]; then
    echo "Uploading to the production PyPI server..."
    python -m twine upload dist/*$version*
    rm -rf dist/*.tar.gz
    rm -rf dist/*.whl
else
    echo "Invalid tag specified. Available options are 'test' or 'prod'."
    exit 1
fi



# End of script