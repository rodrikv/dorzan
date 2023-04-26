# Dorzan

A quick xray setup for connecting to the internet using [Marzban](https://github.com/Gozargah/Marzban) dashboard for management and Cloudflare DNS.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Docker
- Python

## Installation

To install the project, follow these steps:

1. Copy the `.env.example` file to `.env` and change the required variables.
2. Run `docker-compose up -d` to start the application.

## Usage

To use the project, follow these steps:

1. If you want to prevent your sub-domain from getting filtered, add `python3 filter.py` to your crontab.
2. To run `filter.py`, you need to install the `dotenv` package. You can install it using either of the following commands:
   - `pip install dotenv`
   - `pip install python-dotenv`

## Contributing

To contribute to the project, follow these steps:

1. Fork this repository.
2. Create a branch: `git checkout -b feature/feature-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the feature branch: `git push origin feature/feature-name`
5. Create a pull request.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the `LICENSE` file for details. You are free to use, modify, and distribute the code as you see fit, as long as you include a copy of the license in your distribution.