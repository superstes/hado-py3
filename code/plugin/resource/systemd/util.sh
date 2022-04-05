#!/usr/bin/env bash

HELP=false

for i in "$@"; do
  case $i in
    -u=*|--unit=*)
      SVC="${i#*=}"
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

if $HELP || [ -z "$SVC" ]
then
  echo "Usage: '-u' => systemd unit name (pe: '-u=networking.service')"
  exit 1
fi
