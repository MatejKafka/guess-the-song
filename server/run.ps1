$env:PORT = 12000

$ErrorActionPreference = "Stop"

Write-Output "Starting ngrok..."
$job = Start-Job -ArgumentList $env:PORT {
	param($port)
	.\bin\ngrok.exe http $port
}

try {
	Write-Host "Waiting for ngrok connection..." -NoNewLine
	while ($true) {
		Start-Sleep 0.5
		$tunnels = Invoke-WebRequest "http://localhost:4040/api/tunnels" | ConvertFrom-Json
		if ($tunnels.tunnels.Length -gt 0) {
			break
		}
		Write-Host "." -NoNewline
	}
	Write-Host ""
	$httpPublicUrl = $tunnels.tunnels[0].public_url
	$wsPublicUrl = $httpPublicUrl.Replace("http://", "wss://").Replace("https://", "wss://")
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
	Write-Output ""
	Write-Output "Server exited, shutting down ngrok..."
	Remove-Job $job -Force
	Write-Output "Ngrok stopped"
	exit $nodeExitCode
}