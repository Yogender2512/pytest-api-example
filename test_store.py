from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

@pytest.fixture  # fixture to create and cleanup
def new_order():
    order_data = {
        "petId": 123,       
        "quantity": 1,
        "status": "placed",
        "complete": False
    }
    response = api_helpers.post_api_data("/store/order", order_data) #To create order
    assert response.status_code == 200
    order = response.json()

    yield order  

    api_helpers.delete_api_data(f"/store/order/{order['id']}") #To delete order

def test_patch_order_by_id(new_order):
    order_id = new_order['id']
    endpoint = f"/store/order/{order_id}"
    patch_data = {"status": "approved"}

    response = api_helpers.patch_api_data(endpoint, patch_data)
    assert response.status_code == 200

    json_response = response.json()
    assert "Order and pet status updated successfully" in json_response.get("message", "") #validate response message

    if "order" in json_response:  # validate response schema if api return order data
        validate(instance=json_response["order"], schema=schemas.order)

@pytest.mark.parametrize("status", ["placed", "approved", "delivered"])
def test_patch_order_status_updates(new_order, status):
    endpoint = f"/store/order/{new_order['id']}"
    patch_data = {"status": status}

    response = api_helpers.patch_api_data(endpoint, patch_data)
    assert response.status_code == 200

    json_response = response.json()
    assert "Order and pet status updated successfully" in json_response.get("message", "")

@pytest.mark.parametrize("invalid_order_id", [-1, 0, 999999])
def test_patch_order_invalid_id(invalid_order_id):
    endpoint = f"/store/order/{invalid_order_id}"
    patch_data = {"status": "approved"}

    response = api_helpers.patch_api_data(endpoint, patch_data)
    assert response.status_code in [400, 404, 405] # Error status codes for invalid order Ids

@pytest.mark.parametrize("invalid_status", ["invalid", "", None])
def test_patch_order_invalid_status(new_order, invalid_status):
    endpoint = f"/store/order/{new_order['id']}"
    patch_data = {"status": invalid_status}

    response = api_helpers.patch_api_data(endpoint, patch_data)
    assert response.status_code == 400 # API will reject inavlid status
