#!/usr/bin/env bash

D_TIMEOUT="0.2"
TIMEOUT="$D_TIMEOUT"
D_PROTO="tcp"
PROTO="$D_PROTO"
UDP_FLAG=""
HELP=false

for i in "$@"; do
  case $i in
    -t=*|--target=*)
      TARGET="${i#*=}"
      shift
      ;;
    -p=*|--port=*)
      PORT="${i#*=}"
      shift
      ;;
    -s=*|--source-ip=*)
      SOURCE_IP="${i#*=}"
      shift
      ;;
    -w=*|--wait=*)
      TIMEOUT="${i#*=}"
      shift
      ;;
    -P=*|--proto=*)
      PROTO="${i#*=}"
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

if $HELP || [ -z "$TARGET" ] || [ -z "$PORT" ]
then
  echo "Usage: '-t' => target ip/hostname (pe: '-t=1.1.1.1')"
  echo "       '-p' => target port (pe: '-p=53')"
  echo "       '-s' => source ip (optional)"
  echo "       '-w' => timeout in seconds (optional, pe: '-w=0.3', default='$D_TIMEOUT')"
  echo "       '-P' => protocol to use (optional, pe: '-P=udp', options='tcp,udp', default='$D_PROTO')"
  echo "       '-h' => show help (optional)"
  exit 1
fi

if [ "$PROTO" == "udp" ]
then
  UDP_FLAG="-u"
fi

if [ -z "$SOURCE_IP" ]
then
  timeout "$TIMEOUT" nc -zv $UDP_FLAG "$TARGET" "$PORT" >/dev/null 2>&1
else
  timeout "$TIMEOUT" nc -zv -s "$SOURCE_IP" $UDP_FLAG "$TARGET" "$PORT" >/dev/null 2>&1
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
