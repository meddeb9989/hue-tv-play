#!/usr/bin/env bash
# Regular Colors
ResetColor="\033[0m"
LightRed="\033[1;31m"
Green="\033[0;32m"
BGreen="\033[1;32m"
LightBlue="\033[1;34m"
Yellow="\033[1;33m"

_print() { printf "${Green}%b${ResetColor}\n" "$1"; }
_error() {
    printf "${LightRed}%b${ResetColor}\n" "$1" >&2
    exit 1
}
_warning() { printf "${Yellow}%b${ResetColor}\n" "$1"; }
_cmd_exists() { command -v "$1" >/dev/null 2>&1; }

_trace() {
    printf "${LightBlue}+ ${*}${ResetColor}\n" >&2
    eval "$*"
}

_container_is_running() {
    [ "$(docker inspect -f '{{.State.Running}}' "$1" 2>/dev/null)" == "true" ]
}

_container_name_to_compose_app() {
    echo "$1" | sed -e "s/^${COMPOSE_PROJECT_NAME}_//" | sed -e "s/_1$//"
}

_start_and_forget() {
    # Run a program in the background (suppressing any output)
    nohup "$@" 1>/dev/null 2>&1 &
    disown
}

_open() {
    if _cmd_exists /usr/bin/open; then
        /usr/bin/open "$@"
    elif _cmd_exists /usr/bin/xdg-open; then
        _start_and_forget /usr/bin/xdg-open "$@"
    else
        _error "Could not find a command to open $*"
    fi
}

docker_compose() {
    _trace COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME COMPOSE_FILE=$COMPOSE_FILE docker-compose "$@"
}

docker_compose_execute() {
    if [ -t 0 ]; then
        LINES=$(tput lines)
        COLUMNS=$(tput cols)
        TERM=xterm-256color
        EXEC_OPTIONS="-e TERM=$TERM -e COLUMNS=$COLUMNS -e LINES=$LINES"
    else
        EXEC_OPTIONS="-T"
    fi
    CONTAINER=$1
    SHELL="bash"
    shift
    if [ $# -eq 0 ]; then
        docker_compose exec $EXEC_OPTIONS $CONTAINER $SHELL
    else
        SHELL_CMD="$*"
        docker_compose exec $EXEC_OPTIONS $CONTAINER $SHELL -c "'$SHELL_CMD'"
    fi
}

list_project_containers() {
    docker ps -q -a --filter="name=^${COMPOSE_PROJECT_NAME}_" "$@"
}

docker_sync()
{
  if _cmd_exists docker-sync; then
    if [ "$1" != "start" ] || ! _container_is_running "ftth360-code-sync"; then
      _trace docker-sync "$@"
    fi
  fi
}
