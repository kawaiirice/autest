#!/bin/bash
pushd $(dirname $0) > /dev/null
export PYTHONPATH=$(pwd):$PYTHONPATH
RED='\033[0;31m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color
if [ ! -f ./env-test/bin/autest ]; then\
        echo -e "${RED}AuTest is not installed! Bootstrapping system...${NC}";\
		./bootstrap.py;\
        echo -e "${GREEN}Done!${NC}";\
	fi
./env-test/bin/autest -D gold_tests $*
ret=$?
popd > /dev/null
exit $ret
