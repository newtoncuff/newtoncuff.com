db_username = "root"  # Replace with your MySQL username
db_password = "Saida"  # Replace with your MySQL password
db_server = "69.48.207.125"  # IP address of your MySQL server
db_port = "3306"  # Default MySQL port
db_name = "newtoncuff_com"  # Replace with your database name
db_driver = "mysql+mysqlconnector"  # SQLAlchemy driver for MySQL

# Construct the full SQLAlchemy database URI
database_connection_uri = (
    f"{db_driver}://{db_username}:{db_password}@{db_server}:{db_port}/{db_name}"
)

print(database_connection_uri)
