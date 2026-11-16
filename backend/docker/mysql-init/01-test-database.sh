#!/bin/sh
# Tworzy osobną bazę dla testów integracyjnych (<nazwa>_test), żeby testy nigdy nie
# dotykały danych w bazie roboczej. Uruchamiane przez obraz MySQL tylko przy pierwszym starcie.
set -e
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<SQL
CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}_test\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}_test\`.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
SQL
