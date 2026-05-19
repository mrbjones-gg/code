param(
    [string]$Server = "localhost",
    [string]$Database = "master"
)

$username = "admin"
$password = "Th111sisjkjk"

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
