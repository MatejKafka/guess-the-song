$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot


Write-Output "Starting ngrok..."
$job = Start-Job {
	.\bin\ngrok.exe start -config ./ngrok.yml server | % {
		$parsed = ConvertFrom-Json $_
		if (3 -eq @($parsed | Get-Member @("msg", "url", "addr")).Length -and $parsed.msg -eq "started tunnel") {
			# we found the log containing URL
			echo @{Public=$parsed.url; Local=$parsed.addr}
		}
	}
}

Function Wait-JobOutput($job, $pollPeriod = 0.1) {
	do {
		Start-Sleep $pollPeriod
		$output = Receive-Job $job
	} while ($output -eq $null)
	return $output
}

$oldEnvPort = $env:PORT
try {
	Write-Host "Waiting for ngrok connection..."
	$urls = Wait-JobOutput $job
	$wsPublicUrl = "wss://" + $urls.Public.split("://")[1]
	$env:PORT = $urls.Local.Split(":")[2]
} catch {
	Remove-Job $job -Force
	throw $_
}

Write-Output ""
Write-Output ("URL (copied to clipboard): " + $wsPublicUrl)
Write-Output ""
Set-Clipboard $wsPublicUrl

try {
	node .
} finally {
	$nodeExitCode = $LastExitCode
	$env:PORT = $oldEnvPort
	Write-Output ""
	Write-Output "Server exited, shutting down ngrok..."
	Remove-Job $job -Force
	Write-Output "Ngrok stopped"
	exit $nodeExitCode
}