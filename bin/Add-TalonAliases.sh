#!/bin/bash

# Very effective way to get script dir. Taken from a stackexchange comment by Dave Dopson
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

bindir=$SCRIPT_DIR
inidir=$(dirname $SCRIPT_DIR)

alias talon="$bindir/talon -c $inidir/talon.ini"
alias talon-gui="$bindir/talon-gui -c $inidir/talon.ini"
alias tlist="$bindir/tlist -c $inidir/talon.ini"
alias tmdupdate="$bindir/tmdupdate -c $inidir/talon.ini"
alias trecord="$bindir/trecord -c $inidir/talon.ini"
alias tsplit="$bindir/tsplit"
alias tweather="$bindir/tweather -c $inidir/talon.ini"
