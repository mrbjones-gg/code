param(
    [string]$Server = "localhost",
    [string]$Database = "master"
)

$username = "admin"

# Read password from environment variable to avoid storing secrets in source control
$password = "B0ng0!2!"
if (-not $password) {
    Write-Error "Environment variable DB_PASSWORD is not set. Set it before running the script."
    exit 1
}

$connectionString = "Server=$Server;Database=$Database;User Id=$username;Password=$password;Encrypt=False;"

try {
    $connection = New-Object System.Data.SqlClient.SqlConnection $connectionString
    $connection.Open()
    Write-Host "Connected to database '$Database' on server '$Server' as user '$username'." -ForegroundColor Green
    $connection.Close()
} catch {
    Write-Error "Failed to connect to the database: $_"
    exit 1
}
