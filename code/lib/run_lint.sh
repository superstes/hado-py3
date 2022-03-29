#!/bin/bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

# exclusions:
#   C0103 => short and upper-case variables will be used
#   C0114-C0116 => inline documentation might be added later on
#   R0902 => some classes will use more than 5 attributes
#   R0903 => sometimes classes are used for convenience
#   R1705,R1723 => there's a reason for 'else' after breaks and returns.. (;

echo "### Linting library ###"
pylint hado/**/*.py --max-line-length=120 --disable=C0103,C0114,C0115,C0116,R0902,R0903,R1705,R1723

# test exclusions:
#   C0103 => short and upper-case variables will be used
#   C0114-C0116 => inline documentation might be added later on
#   C0415 => importing in functions for testing
#   R0201 => methods used for pytest grouping
#   W0212 => accessing protected methods for testing

echo "### Linting unit tests ###"
pylint ../test/**/*.py --max-line-length=120 --disable=C0103,C0114,C0115,C0116,C0415,R0201,W0212
