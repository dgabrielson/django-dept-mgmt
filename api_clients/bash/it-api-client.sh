#!/bin/bash
### IT Mgmt API bash script
### (c) 2015 Dave Gabrielson <dave.gabrielson@umanitoba.ca> 

### This is a minimal bash API client, using only standard tools found
### in the OS X installer/rescue environment.

### This link may be helpful for keychain integration on OS X:
###     http://blog.macromates.com/2006/keychain-access-from-shell/

### Scripts that source or include this script will probably only want to use
### the following functions:
### * it-api-cn
### * it-api-clientidentifier <key>


BASE_URL="https://www.stats.umanitoba.ca/it-mgmt/api/v1/"
#BASE_URL="http://localhost:8000/it-mgmt/api/v1/"
CURL="/usr/bin/curl --connect-timeout 2 -fsLX"
ACCEPT_HEADER="Accept: application/json; indent=4"


# get a particular value from lines of the format "key": "value"
function get_value()
{
    local key=$1
    grep "${key}" | cut -f 4 -d \"
}


HOST_ID=$(ioreg -rd1 -c IOPlatformExpertDevice | get_value UUID)


function space_fix()
{
    tr '\n' ' ' | tr '\t' ' ' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | tr -s ' ' 
}


function get_auth_token()
{
    #printf "33a1080ded702a393295bdb381f7aee439922d8f"
    cat "/var/db/.it-api-token" 2>/dev/null
}


function it-api-token-auth()
{
    local user=$1
    local password=""
    
    if [ -z "${user}" ]; then
        user=$(whoami)
    fi
    echo "username=${user}"
    echo -n "Password: "
    read -s password
    echo
    
    ${CURL} POST "${BASE_URL}api-token-auth/" -H "${ACCEPT_HEADER}" \
         --data-urlencode "username=${user}" \
         --data-urlencode "password=${password}" | get_value token
}


function it-api-url()
{
    local AUTH_HEADER="Authorization: Token $(get_auth_token)"
    local METHOD=$1
    local URL=$2
    shift 2
    
    ${CURL} ${METHOD} "${URL}" -H "${AUTH_HEADER}" -H "${ACCEPT_HEADER}" "$@"
}


function it-api()
{
    local METHOD=$1
    local RESOURCE=$2
    shift 2
    
    it-api-url ${METHOD} "${BASE_URL}${RESOURCE}" "$@"
}


function it-api-create()
{
    local RESOURCE=$1
    shift 1
    
    it-api POST "${RESOURCE}" "$@"
}


function it-api-retrieve()
{
    local RESOURCE=$1
    shift 1
    
    it-api GET "${RESOURCE}" "$@"
}


# Like retrieve, but with a query string parameter
function it-api-search()
{
    local RESOURCE=$1
    local QUERY=$2
    shift 2
    
    it-api GET "${RESOURCE}?${QUERY}" "$@"
}




function it-api-update()
{
    local RESOURCE=$1
    shift 1
    
    # use patch to support partial updates when an item already exists.
    it-api PATCH "${RESOURCE}" "$@"
}


function it-api-delete()
{
    local RESOURCE=$1
    shift 1
    
    it-api DELETE "${RESOURCE}" "$@"
}



function get_hardware_value()
{
    local data="${1}"
    local key="${2}"
    printf "${data}" | grep "${key}" | cut -f 2 -d :
}


function get-network-type()
{
    # See it_mgmt.models.NetworkInterface.TypeCodes
    local port=$1
    if echo "${port}" | grep ^Ethernet &> /dev/null; then
        echo "e"
    fi
    if echo "${port}" | grep ^Wi-Fi &> /dev/null; then
        echo "w"
    fi
    if echo "${port}" | grep ^Bluetooth &> /dev/null; then
        echo "b"
    fi
    if echo "${port}" | grep ^Thunderbolt &> /dev/null; then
        echo "t"
    fi
}


function create-network-ports()
{
    local computer_url=$1
    local line=""
    local port=""
    local devname=""
    local ether=""
    local typecode=""
    local primary=""
    
    /usr/sbin/networksetup -listallhardwareports | \
    while read line ; do
        if echo "${line}" | grep '^Hardware Port:' &>/dev/null; then
            port=$(echo "${line}" | cut -f 2 -d : | space_fix)
            read line
            devname=$(echo "${line}" | cut -f 2 -d : | space_fix)
            read line
            ether=$(echo "${line}" | cut -f 2- -d : | space_fix)
            typecode=$(get-network-type "${port}")
            if [ -z "${typecode}" ]; then
                echo "Unknown port type: ${port}" 2>/dev/null
            else
                if [ "${ether}" != "N/A" ]; then
                    primary=""
                    if [ "${typecode}" == "e" ]; then
                        primary="--data-urlencode primary=true"
                    fi
                    it-api-create networkinterfaces/ ${primary} \
                        --data-urlencode "computer=${computer_url}" \
                        --data-urlencode "name=${devname}" \
                        --data-urlencode "type=${typecode}" \
                        --data-urlencode "mac_address=${ether}"
                fi
            fi
        fi
    done
}


function it-api-create-computer()
{
    local hardware_data="$(system_profiler SPHardwareDataType)"
    local software_data="$(/usr/bin/sw_vers)"
    
    local common_name=$(/usr/sbin/scutil --get ComputerName | space_fix)
    local hardware=$((get_hardware_value "${hardware_data}" Model\ Identifier ; echo -; get_hardware_value "${hardware_data}" Serial\ Number)| space_fix )
    local ram=$(get_hardware_value "${hardware_data}" Memory)
    local processor=$((get_hardware_value "${hardware_data}" Processor\ Name ; echo @; get_hardware_value "${hardware_data}" Processor\ Speed)| space_fix)
    local operating_system=$((get_hardware_value "${software_data}" ProductName ; get_hardware_value "${software_data}" ProductVersion)| space_fix)
    local harddrive=$(get_hardware_value "$(system_profiler -detailLevel mini  SPSerialATADataType)" Capacity | cut -f 1 -d \( | space_fix | sed -e 's/B /B, /' ) 

    local flag=$(it-api-get-or-create flags/ "slug=placeholder" --data-urlencode "verbose_name=Placeholder")
    local flag_url=$(printf "${flag}" | get_value url)
    
    local computer="$(it-api-create computers/ \
        --data-urlencode "common_name=${common_name}" \
        --data-urlencode "hardware=${hardware}" \
        --data-urlencode "host_id=${HOST_ID}" \
        --data-urlencode "ram=${ram}" \
        --data-urlencode "processor=${processor}" \
        --data-urlencode "operating_system=${operating_system}" \
        --data-urlencode "harddrive=${harddrive}" \
        --data-urlencode "flags=${flag_url}")"
    local url=$(printf "${computer}" | get_value url)
    create-network-ports "${url}" > /dev/null
    it-api-url GET "${url}"
}


function it-api-get-or-create()
{
    local resource=$1
    local search_filter=$2
    shift 1
    
    local search_results="$(it-api-search ${resource} ${search_filter})"
    local item=""
    if printf "${search_results}" | grep '"count": 0,' &>/dev/null; then
        # create
        item="$(it-api-create "${resource}" --data-urlencode "${search_filter}" "$@")"
    else
        if printf "${search_results}" | grep '"count": 1,' &>/dev/null; then
            local url=$(printf "${search_results}" | get_value url)
            item="$(it-api-url GET ${url})"
        else
            if printf "${search_results}" | grep '"count":' &>/dev/null; then
                echo "MULTIPLE ITEMS FOUND: ${resource} ${search_filter}" 1>&2
                return 22   # EINVAL - Invalid Argument
            else
                echo "NO AUTH" 1>&2
                return 13   # EACCES - Permission denied
            fi
        fi
    fi
    printf "${item}"
}


# Get a computer.  Create a placeholder if it doesn't exist.
function it-api-computer()
{
    local computer_search="$(it-api-search computers/ host_id=${HOST_ID})"
    local computer=""
    local url=""
    if printf "${computer_search}" | grep '"count": 0,' &>/dev/null; then
        computer="$(it-api-create-computer)"
    else
        if printf "${computer_search}" | grep '"count": 1,' &>/dev/null; then
            local url=$(printf "${computer_search}" | get_value url)
            computer="$(it-api-url GET ${url})"
        else
            if printf "${computer_search}" | grep '"count":' &>/dev/null; then
                echo "MULTIPLE ITEMS FOUND: computers/ host_id=${HOST_ID}" 1>&2
                return 22   # EINVAL - Invalid Argument
            else
                echo "NO AUTH" 1>&2
                return 13   # EACCES - Permission denied
            fi
        fi
    fi
    printf "${computer}"
}


function it-api-clientidentifier()
{
    local key="$1"
    
    it-api GET "clientidentifiers/?computer__host_id=${HOST_ID}&key=${key}" | get_value value
}


function it-api-cn()
{
    it-api-computer | get_value common_name
}


### END IT Mgmt API bash script
