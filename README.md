# signal-cli-rest-api
signal-cli-rest-api is a wrapper around [signal-cli](https://github.com/AsamK/signal-cli) and allows you to interact with it through http requests.

This is a fork of the original repository by [SebastianLuebke](https://github.com/SebastianLuebke/signal-cli-rest-api). It comes with additional features:
* Dockerfile with unprivileged user
* String escaping to prevent shell injections
* API endpoint for the Grafana Webhook notification channel

## Running the Docker image

`docker run -p 8000:8000 -v /path/to/your/signal/dir:/srv/signal/.local/share/signal-cli signal-cli-rest-api`

