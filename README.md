# docker-mqttsms
Шлюз между mqtt и sms.
Sms отправляются через gammu (порт /dev/ttyUSB0)

Переменные окружения, которые используются в контейнере
- MQQT_HOST
- MQTT_PORT
- MQTT_USER
- MQTT_PWD
- MQTT_TOPIC - начальный топик для обмена сообщениями (по умолчанию /sms/). Внутри топики 
-- send - отправка sms
-- send/feedback - результат отправки sms
-- receive - получение sms
-- receive/<number> - sms по номеру телефона, при этом спец символы заменены на подчеркивание  

