# Run PGAdmin
- docker-compose -f docker-compose.pgadmin.yml -p pgadmin up --build
# How to use this project?
## Running on Development
### Up and Build
- docker-compose -f docker-compose.dev.yml -p auto-test-app-dev up --build
### Create database
- docker-compose -f docker-compose.dev.yml -p auto-test-app-dev exec web python manage.py create_db
- docker-compose -f docker-compose.dev.yml -p auto-test-app-dev exec web python manage.py seed_db
### Check database
- docker-compose -f docker-compose.dev.yml -p auto-test-app-dev exec db psql --username=hello_flask --dbname=hello_flask_dev
### Open Browser
- http://127.0.0.1:5000/
### Logging
- docker-compose -f docker-compose.dev.yml logs -f
### Down
- docker-compose -f docker-compose.dev.yml -p auto-test-app-dev down --v

## Running on Production
### Up and Build
- docker-compose -f docker-compose.prod.yml -p auto-test-app-prod up --build
### Create database
- docker-compose -f docker-compose.prod.yml -p auto-test-app-prod exec web python manage.py create_db
- docker-compose -f docker-compose.prod.yml -p auto-test-app-prod exec web python manage.py seed_db
### Check database
- docker-compose -f docker-compose.prod.yml -p auto-test-app-prod exec db psql --username=hello_flask --dbname=hello_flask_prod
### Open Browser
- Running on local with url: http://127.0.0.1:1337
- Running on another machine with url: http://{ip machine local}:1337
### Logging
- docker-compose -f docker-compose.prod.yml logs -f
### Down
- docker-compose -f docker-compose.prod.yml -p auto-test-app-prod down --v
