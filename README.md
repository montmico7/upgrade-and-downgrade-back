README
This repository contains a command-line interface (CLI) for managing customer subscriptions. The CLI allows you to set up the necessary dependencies, upgrade or downgrade customer subscriptions, and perform various actions related to subscription management.

Prerequisites
Before using the CLI, ensure that you have the following dependencies installed:

Python 3.x
pip
Setup
To set up the CLI and install the required dependencies, run the following command:

shell
Copy code
$ ./cli setup
This command will install the necessary Python packages specified in the requirements.txt file.

Usage
Upgrading a Subscription
To upgrade a customer's subscription, use the following command:

php
Copy code
$ ./cli upgrade <customer_id> <subscription_level>
Replace <customer_id> with the ID of the customer whose subscription you want to upgrade and <subscription_level> with the desired new subscription level (valid options: "free", "basic", "premium").

Downgrading a Subscription
To downgrade a customer's subscription, use the following command:

php
Copy code
$ ./cli downgrade <customer_id> <subscription_level>
Replace <customer_id> with the ID of the customer whose subscription you want to downgrade and <subscription_level> with the desired new subscription level (valid options: "free", "basic", "premium").

Examples
Upgrade a customer with ID 123 to the premium subscription level:

shell
Copy code
$ ./cli upgrade 123 premium
Downgrade a customer with ID 456 to the basic subscription level:

shell
Copy code
$ ./cli downgrade 456 basic
Configuration
The CLI uses a configuration file named config.ini to store the API URL. Update the API_URL value in the config.ini file to match your API endpoint.

Dependencies
The required dependencies for this CLI are listed in the requirements.txt file. You can install them manually or use the provided setup command to install them automatically.

Notes
The CLI communicates with the API endpoint specified in the config.ini file to manage customer subscriptions.
The CLI performs various checks and validations to ensure that the upgrade or downgrade operations are valid and consistent.
Error messages will be displayed if any issues occur during the upgrade or downgrade process.
The CLI handles common connection errors and provides appropriate error messages.
