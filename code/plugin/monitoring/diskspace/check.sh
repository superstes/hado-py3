#!/usr/bin/env bash

D_MOUNT="/"
MOUNT="$D_MOUNT"
D_THRESHOLD=95
THRESHOLD=$D_THRESHOLD
HELP=false
DEBUG=false

for i in "$@"; do
  case $i in
    -m=*|--mount=*)
      MOUNT="${i#*=}"
      shift
      ;;
    -t=*|--threshold=*)
      THRESHOLD="${i#*=}"
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

if $HELP
then
  echo "Usage: '-m' => mount path (optional, pe: '-m=/mnt/test', default='$D_MOUNT')"
  echo "       '-t' => threshold as percentage (optional, pe: '-t=90', default='$D_THRESHOLD')"
  echo "       '-h' => show help (optional)"
  exit 1
fi

result=$(df "$MOUNT" 2>/dev/null | grep '/' | awk '{ print $5}' | sed 's/%//g')

# shellcheck disable=SC2181
if [ "$?" == "0" ]
then
  if $DEBUG
  then
    echo "Result: '$result' < $THRESHOLD"
  fi
  if [ -z "$result" ] || (( result > THRESHOLD ))
  then
    echo 0
    exit 1
  else
    echo 1
    exit 0
  fi
else
  if $DEBUG
  then
    echo 'Got error finding device!'
  fi
  echo 0
  exit 1
fi

