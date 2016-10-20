# Prototype work for TSQA replacement #

to run tests (quick easy way)

cd tests
./autest.sh --ats-bin <dirto/binats> --sandbox ~/sb

This should run the tests. Make sure that you have a build of Traffic server installed to some location. The --sandbox option is needed as a few tests require the use of unix domain sockets. There is a path size limit for creating such sockets.

to run the more advance way

cd test
./bootstrap
source env_test/bin/activate
cd gold_tests
autests ----ats-bin <dirto/binats> --sandbox ~/sb