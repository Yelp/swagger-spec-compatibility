#!/bin/bash
set -euxo pipefail -o posix -o functrace
# The pyenv changelog is available on # https://github.com/pyenv/pyenv/blob/master/CHANGELOG.md
# The selected pyenv version has 2.7.15, 3.5.6, 3.6.6, 3.7.0 versions available
MIN_PYENV_VERSION=1.2.7

GENERATED_ENVIRONMENT_FILE=${HOME}/generated-environment.sh
# Ensure that the file is cleaned (if case it was already present)
echo -n '' > ${GENERATED_ENVIRONMENT_FILE}
echo '#!/bin/bash' >> ${GENERATED_ENVIRONMENT_FILE}
echo 'set -x' >> ${GENERATED_ENVIRONMENT_FILE}

# Define the python version to use for each tox environment
case "${TOXENV}" in
    pre-commit) PYTHON=3.6 ;;
    py27) PYTHON=2.7 ;;
    py35) PYTHON=3.5 ;;
    py36) PYTHON=3.6 ;;
    py37) PYTHON=3.7 ;;
    docs) PYTHON=3.6 ;;
    *) echo "${TOXENV} is not in the list of the known python versions, please fix .travis.yml file and/or update $0 content" > /dev/stderr; exit 1 ;;
esac

if [ "${TRAVIS_OS_NAME}" == "osx" ]; then
    # Ensure that pyenv is installed and install it if missing
    if ! find $(brew --prefix)/Cellar/pyenv/*/bin/pyenv -quit; then
      time brew install pyenv
    fi

    # Ensure that pyenv is at least at version ${MIN_PYENV_VERSION} and upgrade it if needed
    if ! pyenv --version | cut -d' ' -f 2 | python -c "from distutils.version import LooseVersion; exit(LooseVersion(raw_input()) < LooseVersion('${MIN_PYENV_VERSION}'))"; then
      time brew upgrade pyenv
      time brew cleanup
    fi

    # Extract the most recent python version from pyenv
    PYTHON=$(pyenv install -l | grep -E "^\s+(${PYTHON}.[0-9]+)\$" | tail -n 1 | tr -d '[:space:]')

    # Ensure that the required python version is installed and install it if missing
    if ! pyenv versions --bare | grep -q "^${PYTHON}\$"; then
      # According to pyenv homebrew recommendations (https://github.com/yyuu/pyenv/wiki#suggested-build-environment)
      time brew install openssl readline sqlite3 xz zlib
      time pyenv install ${PYTHON}
      # Register pyenv
      pyenv local ${PYTHON}
    fi
    echo "export PYTHON=${PYTHON}" >> ${GENERATED_ENVIRONMENT_FILE}
    echo 'export PYENV_VERSION=${PYTHON}' >> ${GENERATED_ENVIRONMENT_FILE}
    echo 'export PATH="${HOME}/.pyenv/shims:${PATH}"' >> ${GENERATED_ENVIRONMENT_FILE}
fi

echo 'set +x' >> ${GENERATED_ENVIRONMENT_FILE}

# Activate all the configured environments
source ${GENERATED_ENVIRONMENT_FILE}

# Install the python tools needed on all the OSes
pip install codecov tox

echo "Installed tools and versions"
python -c "import sys;print(sys.version)"
pip --version
codecov --version
tox --version
