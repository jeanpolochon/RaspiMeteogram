<?php
/**
 * @param callback {String} The name of the JSONP callback to pad the JSON within
 */

// Get the parameters
$callback = $_GET['callback'];
if (!preg_match('/^[a-zA-Z0-9_]+$/', $callback)) {
	die('Invalid callback name');
}

// Get database parameters
$ini = parse_ini_file('/home/pi/RaspiMeteogram/db.conf');
$servername = "localhost";
$username = $ini['username'];
$password = $ini['password'];
$dbname = $ini['database'];
$table = $ini['table'];


// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 


// Get data
$sql = "SELECT tdatetime, temperature, pressure, humidity FROM $table ";
$result = $conn->query($sql) or die(mysql_error());
$rows = array();
while ($row = $result->fetch_assoc()) {
	extract($row);
	$rows[] = "[moment('$tdatetime').valueOf(),$temperature,$pressure,$humidity]";
}

// Close connection
$conn->close();

// Print data
header('Content-Type: text/javascript');
echo $callback ."([\n" . join(",\n", $rows) ."\n]);";
?>
