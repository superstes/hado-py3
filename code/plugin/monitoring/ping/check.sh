#!/usr/bin/env bash

D_TIMEOUT="0.2"
TIMEOUT="$D_TIMEOUT"
HELP=false

for i in "$@"; do
  case $i in
    -t=*|--target=*)
      TARGET="${i#*=}"
      shift
      ;;
    -s=*|--source=*)
      SOURCE="${i#*=}"
      shift
      ;;
    -w=*|--wait=*)
      TIMEOUT="${i#*=}"
      shift
      ;;
    -h*|--help*|?)
      HELP=true
      shift
      ;;
    *)
      ;;
  esac
done

if $HELP || [ -z "$TARGET" ]
then
  echo "Usage: '-t' => ping target (pe: '-t=1.1.1.1')"
  echo "       '-s' => ping source ip (optional)"
  echo "       '-w' => timeout in seconds (optional, pe: '-w=0.3', default='$D_TIMEOUT')"
  echo "       '-h' => show help (optional)"
  exit 1
fi

if [ -z "$SOURCE" ]
then
  timeout "$TIMEOUT" ping -c1 "$TARGET" -q >/dev/null 2>&1
else
  timeout "$TIMEOUT" ping -c1 "$TARGET" -I "$SOURCE" -q >/dev/null 2>&1
fi

# shellcheck disable=SC2181
if [ "$?" == "0" ]
then
  echo 1
  exit 0
else
  echo 0
  exit 1
fi
