#!/bin/bash

TIMEOUT="0.2"

for i in "$@"; do
  case $i in
    -t=*|--target=*)
      TARGET="${i#*=}"
      shift # past argument=value
      ;;
    -s=*|--source=*)
      SOURCE="${i#*=}"
      shift # past argument=value
      ;;
    -w=*|--wait=*)
      TIMEOUT="${i#*=}"
      shift # past argument=value
      ;;
    *)
      ;;
  esac
done

if [ -z "$TARGET" ]
then
  echo "Error: No arguments supplied!"
  echo "Usage: '-t' => ping target (pe: '-t=1.1.1.1')"
  echo "       '-s' => ping source ip (optional)"
  echo "       '-w' => timeout in seconds (optional, pe: '-w=0.3', default=$TIMEOUT)"
  exit 1
fi

if [ -z "$SOURCE" ]
then
  timeout "$TIMEOUT" ping -c1 "$TARGET" -q >/dev/null 2>/dev/null
else
  timeout "$TIMEOUT" ping -c1 "$TARGET" -I "$SOURCE" -q >/dev/null 2>/dev/null
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
