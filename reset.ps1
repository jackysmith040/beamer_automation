<#
.SYNOPSIS
    Resets the Beamer & Thesis automation workspace so you can start a fresh project.
.DESCRIPTION
    Archives current work in archive/, clears input/, digestion/, and output/,
    reinitializes the folder structures, and leaves your TeX compiler and templates intact.
.EXAMPLE
    .\reset.ps1
.EXAMPLE
    .\reset.ps1 -NoBackup
.EXAMPLE
    .\reset.ps1 -DryRun
#>

param(
    [switch]$NoBackup,
    [switch]$ClearTemplates,
    [switch]$CleanInbox,
    [switch]$DryRun
)

$argsList = @()
if ($NoBackup) { $argsList += "--no-backup" }
if ($ClearTemplates) { $argsList += "--clear-templates" }
if ($CleanInbox) { $argsList += "--clean-inbox" }
if ($DryRun) { $argsList += "--dry-run" }

python reset_pipeline.py @argsList
