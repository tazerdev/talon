#!/bin/bash

# Very effective way to get script dir. Taken from a stackexchange comment by Dave Dopson
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

bindir=$SCRIPT_DIR
etcdir=$(dirname $SCRIPT_DIR)/etc

alias talon="$bindir/talon -c $etcdir/talon.ini"
alias talon-gui="$bindir/talon-gui -c $etcdir/talon.ini"
alias tlist="$bindir/tlist -c $etcdir/talon.ini"
alias tmdupdate="$bindir/tmdupdate -c $etcdir/talon.ini"
alias trecord="$bindir/trecord -c $etcdir/talon.ini"
alias tweather="$bindir/tweather -c $etcdir/talon.ini"
