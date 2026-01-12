$etcdir = [string](Get-Item $PSScriptRoot).Parent + "\"
$bindir = [string](Get-Item $PSScriptRoot).Parent + "\bin\"

function talon {
    $curargs = $args -join " "
    Invoke-Expression ("$env:VIRTUAL_ENV" + "\Scripts\python.exe" + " " + "$bindir" + "talon" + " " + "-c $etcdir" + "talon.ini" + " " + "$curargs")
}

function talon-gui {
    $curargs = $args -join " "
    Invoke-Expression ("$env:VIRTUAL_ENV" + "\Scripts\python.exe" + " " + "$bindir" + "talon-gui" + " " + "-c $etcdir" + "talon.ini" + " " + "$curargs")
}

function tlist {
    $curargs = $args -join " "
    Invoke-Expression ("$env:VIRTUAL_ENV" + "\Scripts\python.exe" + " " + "$bindir" + "tlist" + " " + "-c $etcdir" + "talon.ini" + " " + $curargs)
}

function tmdupdate {
    $curargs = $args -join " "
    Invoke-Expression ("$env:VIRTUAL_ENV" + "\Scripts\python.exe" + " " + "$bindir" + "tmdupdate" + " " + "-c $etcdir" + "talon.ini" + " " + $curargs)
}

function trecord {
    $curargs = $args -join " "
    Invoke-Expression ("$env:VIRTUAL_ENV" + "\Scripts\python.exe" + " " + "$bindir" + "trecord" + " " + "-c $etcdir" + "talon.ini" + " " + $curargs)
}

function tsplit {
    $curargs = $args -join " "
    Invoke-Expression ("$env:VIRTUAL_ENV" + "\Scripts\python.exe" + " " + "$bindir" + "tsplit" + " " + $curargs)
}

function tweather {
    $curargs = $args -join " "
    Invoke-Expression ("$env:VIRTUAL_ENV" + "\Scripts\python.exe" + " " + "$bindir" + "tweather" + " " + "-c $etcdir" + "talon.ini" + " " + $curargs)
}