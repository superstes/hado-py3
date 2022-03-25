#!/bin/bash

TIMEOUT="0.2"
PROTOCOL="tcp"
UDP_FLAG=""

for i in "$@"; do
  case $i in
    -t=*|--target=*)
      TARGET="${i#*=}"
      shift # past argument=value
      ;;
    -p=*|--port=*)
      PORT="${i#*=}"
      shift # past argument=value
      ;;
    -s=*|--source-ip=*)
      SOURCE_IP="${i#*=}"
      shift # past argument=value
      ;;
    -w=*|--wait=*)
      TIMEOUT="${i#*=}"
      shift # past argument=value
      ;;
    -P=*|--proto=*)
      PROTOCOL="${i#*=}"
      shift # past argument=value
      ;;
    *)
      ;;
  esac
done

if [ -z "$TARGET" ] || [ -z "$PORT" ]
then
  echo "Error: No arguments supplied!"
  echo "Usage: '-t' => target ip/hostname (pe: '-t=1.1.1.1')"
  echo "       '-p' => target port (pe: '-p=53')"
  echo "       '-s' => source ip (optional)"
  echo "       '-w' => timeout in seconds (optional, pe: '-w=0.3', default=$TIMEOUT)"
  echo "       '-P' => protocol to use (optional, pe: '-p=udp', options='tcp,udp', default=$PROTOCOL)"
  exit 1
fi

if [ "$PROTO" == "udp" ]
then
  UDP_FLAG="-u"
fi

if [ -z "$SOURCE_IP" ]
then
  timeout "$TIMEOUT" nc -zv $UDP_FLAG "$TARGET" "$PORT" >/dev/null 2>/dev/null
else
  timeout "$TIMEOUT" nc -zv -s "$SOURCE_IP" $UDP_FLAG "$TARGET" "$PORT" >/dev/null 2>/dev/null
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
