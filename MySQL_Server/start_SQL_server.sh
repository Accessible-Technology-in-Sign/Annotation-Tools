docker run --name annotation_mysql -e MYSQL_ROOT_PASSWORD=annotate -e MYSQL_DATABASE=annotations_db -p 3306:3306 -d mysql:8.0

