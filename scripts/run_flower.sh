DJANGO_DEV_PORT="$(python -c 'import config;print(config.DJANGO_DEV_PORT)')"
echo "Django Port:"
echo $DJANGO_DEV_PORT

docker exec -ti gold-digger-dev-$DJANGO_DEV_PORT sh -c "celery -A GoldDigger flower --port=5555"