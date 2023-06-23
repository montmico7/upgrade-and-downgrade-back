import datetime
import requests
import click
import configparser

# Define available subscription levels
SUBSCRIPTION_LEVELS = ["free", "basic", "premium"]

# Define messages for downgrade status codes
DOWNGRADE_MESSAGES = {
    200: "Customer already has the specified subscription.",
    204: "Subscription downgrade successful.",
    404: "Customer with ID {customer_id} not found.",
    400: "Downgrade failed: Invalid subscription level.",
    500: "Subscription downgrade failed.",
}

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the API URL
api_url = config.get('DEFAULT', 'API_URL')


VALID_UPGRADES = {
    "premium": ["basic", "free"],
    "basic": ["free"]
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
    
def downgrade_subscription(customer_id: str, subscription_level: str) -> int:
    """
    Downgrades the subscription level of a customer to the specified level.

    Args:
        customer_id (str): The ID of the customer whose subscription will be downgraded.
        subscription_level (str): The desired subscription level to downgrade to.

    Returns:
        int: The HTTP status code of the request:
            - 200 if the customer already has the specified subscription.
            - 204 if the downgrade was successful.
            - 400 if the customer's current subscription is 'free', or if the specified subscription level is invalid.
            - 404 if the customer ID or subscription is not found.
            - 500 if the update was unsuccessful.

    Raises:
        ValueError: If the specified subscription level is not one of the allowed levels.

    """   
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

    # Return 404 if customer has no subscription or if the subscription is not found
    if not current_subscription:
        return 404

    # Return 200 if the customer already has the specified subscription
    if current_subscription == subscription_level:
        return 200

    # Return 400 if the customer's current subscription is free or if the downgrade level is invalid
    if current_subscription == 'free':
        return 400

    # Verify if the target subscription is reachable for an downgrade
    if not verify_subscription_level(current_subscription, subscription_level):
        return 400

    # Update customer data
    data['SUBSCRIPTION'] = subscription_level
    data['DOWNGRADE_DATE'] = str(datetime.datetime.now())

    if subscription_level == "free":
        # If the requested subscription level is free, disable all premium features
        data['ENABLED_FEATURES'] = {feature: False for feature in data['ENABLED_FEATURES']}

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
    
@click.command()
@click.argument("customer_id")
@click.argument("subscription_level")
def downgrade_cli(customer_id: str, subscription_level: str) -> None:
    """
    CLI function for downgrading a customer's subscription.

    Args:
        customer_id (str): The ID of the customer whose subscription will be downgraded.
        subscription_level (str): The desired subscription level to downgrade to.

    Returns:
        None.

    """
    try:
        status_code = downgrade_subscription(customer_id, subscription_level)
        if status_code == 200:
            print(f"Customer already has a {subscription_level} subscription.")
        elif status_code == 204:
            print("Subscription downgraded successfully.")
        elif status_code == 404:
            print(f"Customer with ID {customer_id} not found.")
        elif status_code == 400:
            print("Downgrade failed:", status_code)
        else:
            print("Downgrade failed with status code:", status_code)
    except requests.exceptions.ConnectionError:
        print("Connection error: Unable to connect to server.")

if __name__ == "__main__":
    downgrade_cli()
