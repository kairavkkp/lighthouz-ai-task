export $(grep -v '^#' .env | xargs)
flask --app app.py --debug run
