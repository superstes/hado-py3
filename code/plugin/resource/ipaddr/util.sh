#!/usr/bin/env bash

for i in "$@"; do
  case $i in
    -i=*|--ip=*)
      IP="${i#*=}"
      shift # past argument=value
      ;;
    -d=*|--dev=*)
      DEV="${i#*=}"
      shift # past argument=value
      ;;
    *)
      ;;
  esac
done

if [ -z "$IP" ] || [ -z "$DEV" ]
then
  echo "Error: Not enough arguments supplied!"
  echo "Usage: '-i' => ip address (pe: '-i=10.10.4.2')"
  echo "       '-d' => device to add the ip to (pe: '-d=eno1')"
  exit 1
fi


function get_ip_with_cidr() {
  ip="$1"

  regex_ipv4="(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
  regex_ipv6="(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"

  if echo "$ip" | grep -q '/'
  then
    ip_with_cidr="$ip"
  elif echo "$ip" | grep -q -E "$regex_ipv4"
  then
    ip_with_cidr="${ip}/32"
  elif echo "$ip" | grep -q -E "$regex_ipv6"
  then
    ip_with_cidr="${ip}/128"
  fi

  echo "$ip_with_cidr"
}

IP_CIDR=$(get_ip_with_cidr "$IP")
