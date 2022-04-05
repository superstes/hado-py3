#!/usr/bin/env bash
set -e

D_TIMEOUT="0.2"
TIMEOUT="$D_TIMEOUT"
D_SRV="1.1.1.1"
SRV="$D_SRV"
D_TYPE="A"
TYPE="$D_TYPE"
D_PROTO="udp"
PROTO="$D_PROTO"
PROTO_FLAG="-U"
DEBUG=false
HELP=false

for i in "$@"; do
  case $i in
    -r=*|--record=*)
      RECORD="${i#*=}"
      shift
      ;;
    -c=*|--compare=*)
      COMPARE="${i#*=}"
      shift
      ;;
    -s=*|--nameserver=*)
      SRV="${i#*=}"
      shift
      ;;
    -t=*|--record-type=*)
      TYPE="${i#*=}"
      shift
      ;;
    -w=*|--wait=*)
      TIMEOUT="${i#*=}"
      shift
      ;;
    -p=*|--proto=*)
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

if $HELP || [ -z "$RECORD" ] || [ -z "$COMPARE" ]
then
  echo "Usage: '-r' => record to query (pe: '-r=google.com')"
  echo "       '-c' => value to compare (pe: '-c=4.34.20.3')"
  echo "       '-t' => type of record to query (optional, pe: '-t=MX', default='$D_TYPE')"
  echo "       '-s' => nameserver to use (optional, pe: '-s=192.168.0.1', default='$D_SRV')"
  echo "       '-w' => timeout in seconds (optional, pe: '-w=0.3', default='$D_TIMEOUT')"
  echo "       '-p' => protocol to use (optional, pe: '-p=tcp', options='tcp,udp', default='$D_PROTO')"
  echo "       '-h' => show help (optional)"
  exit 1
fi

if [ "$PROTO" == "tcp" ]
then
  PROTO_FLAG="-T"
fi

result=$(timeout "$TIMEOUT" host -t "$TYPE" $PROTO_FLAG "$RECORD" "$SRV" | tail -n 1 | rev | cut -d ' ' -f1 | rev)

if [ "$result" == "$COMPARE" ]
then
  echo 1
  exit 0
else
  if $DEBUG
  then
    echo "Result: '$result' != '$COMPARE'"
  fi
  echo 0
  exit 1
fi
