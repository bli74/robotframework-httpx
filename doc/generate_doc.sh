#!/usr/bin/env bash
# I know it's bad but there is no other way to keep docstring working with this decorator
SCRIPT_PATH=`dirname "$0"`
sed -i.bak '/@warn_if_equal_symbol_in_url/d' ${SCRIPT_PATH}/../src/HttpxLibrary/HttpxOnSessionKeywords.py
python -m robot.libdoc ${SCRIPT_PATH}/../src/HttpxLibrary ${SCRIPT_PATH}/HttpxLibrary.html
mv ${SCRIPT_PATH}/../src/HttpxLibrary/HttpxOnSessionKeywords.py.bak ${SCRIPT_PATH}/../src/HttpxLibrary/HttpxOnSessionKeywords.py
