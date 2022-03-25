#!/bin/bash

for i in "$@"; do
  case $i in
    -u=*|--unit=*)
      SVC="${i#*=}"
      shift # past argument=value
      ;;
    *)
      ;;
  esac
done

if [ -z "$SVC" ]
then
  echo "Error: No arguments supplied!"
  echo "Usage: '-u' => systemd unit name (pe: '-u=networking.service')"
  exit 1
fi
