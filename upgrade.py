import datetime
import requests
import click
import configparser

# Define subscription levels and messages
SUBSCRIPTION_LEVELS = ["free", "basic", "premium"]
UPGRADE_MESSAGES = {
    200: "Customer already has the specified subscription.",
    204: "Subscription upgraded successfully.",
    404: "Customer with ID {customer_id} not found.",
    400: "Upgrade failed: Invalid subscription level.",
    500: "Subscription upgrade failed.",
}

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the API URL
api_url = config.get('DEFAULT', 'API_URL')


VALID_UPGRADES = {
    "free": ["basic", "premium"],
    "basic": ["premium"]
}

def verify_subscription_level(current_subscription: str, target_subscription: str) -> bool:
    """
    Verify if the target subscription is reachable for an upgrade.

    Args:
        current_subscription (str): The customer's current subscription level.
        target_subscription (str): The desired subscription level to upgrade to.

    Returns:
        bool: True if the target subscription is reachable for an upgrade, False otherwise.
    """
    if current_subscription == target_subscription:
        return False
    elif target_subscription in VALID_UPGRADES.get(current_subscription, []):
        return True
    else:
        return False

    
def upgrade_subscription(customer_id: str, subscription_level: str) -> int:
    """
    Upgrades a customer's subscription to the specified level.

    Args:
        customer_id (str): The ID of the customer whose subscription to upgrade.
        subscription_level (str): The desired subscription level to upgrade to.

    Returns:
        int: The HTTP status code indicating the result of the operation.
            200 if the customer already has the specified subscription.
            204 if the upgrade was successful.
            400 if the upgrade level is invalid, or if the customer's current subscription is premium.
            404 if the customer or their subscription data could not be found.
            500 if the update failed for an unknown reason.
    """
    
    # Check if subscription level is valid
    if subscription_level not in SUBSCRIPTION_LEVELS:
        raise ValueError(f"Invalid subscription level '{subscription_level}'.")
    
    # Construct the customer data URL
    url = f"{api_url}{customer_id}/"

    # Return status code if request was unsuccessful
    response = requests.get(url)
    if response.status_code != 200:
        return response.status_code

    # Extract data from response
    data = response.json().get('data')
    # Return 404 if data is empty or if subscription is not found
    if not data:
        return 404

    current_subscription = data.get('SUBSCRIPTION')
    if not current_subscription:
        return 404

    # Return 200 if the customer already has the specified subscription
    if current_subscription == subscription_level:
        return 200

    # Return 400 if the customer's current subscription is premium or if the upgrade level is invalid
    if current_subscription == 'premium':
        return 400

    # Verify if the target subscription is reachable for an upgrade
    if not verify_subscription_level(current_subscription, subscription_level):
        return 400

    # Update customer data
    data['SUBSCRIPTION'] = subscription_level
    data['UPGRADE_DATE'] = str(datetime.datetime.now())

    response = requests.put(url, json={"data": data})

    # Check if the update was successful and return status code accordingly
    if response.status_code == 200:
        updated_data = response.json().get('data')
        if updated_data and updated_data['SUBSCRIPTION'] == subscription_level:
            return 204
        else:
            return 500
    else:
        return response.status_code

    
#CLI function to upgrade customer subscription level

@click.command()
@click.argument("customer_id")
@click.argument("subscription_level")
def upgrade_cli(customer_id: str, subscription_level: str) -> None:
    """
    CLI function for upgrading a customer's subscription.

    Args:
        customer_id (str): The ID of the customer whose subscription will be upgraded.
        subscription_level (str): The desired subscription level to upgraded to.

    Returns:
        None.
    """
    try:
        # Call upgrade_subscription function and print appropriate message based on status code
        status_code = upgrade_subscription(customer_id, subscription_level)
        print(UPGRADE_MESSAGES[status_code].format(customer_id=customer_id))
    except ValueError as e:
        # Handle value error if subscription level is invalid
        print("Upgrade failed:", str(e))
    except requests.exceptions.ConnectionError:
        # Handle connection error
        print("Connection error: Unable to connect to server.")

#Call upgrade_cli function if script is executed directly
if __name__ == "__main__":
    upgrade_cli()
