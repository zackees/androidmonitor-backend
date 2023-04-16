#! /bin/bash
set -e
# extract -f from the command line
# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -f|--force)
    FORCE=-f
    shift # past argument
    ;;
    *)    # unknown option
    shift # past argument
    ;;
esac
done
git push $FORCE --mirror
git push $FORCE --mirror https://github.com/zackees/androidmonitor-backend