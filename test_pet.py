from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

def test_pet_schema(): #schema verfication of a single pet
    test_endpoint = "/pets/1" #testing pet with id1 to make sure the response matches 
    response = api_helpers.get_api_data(test_endpoint)
    assert response.status_code == 200
    
    pet_data = response.json()
    # Validate the response schema against the defined schema in schemas.py
    validate(instance=pet_data, schema=schemas.pet)

@pytest.mark.parametrize ("status",["available","sold","pending"]) #test findbystatus endpoint for all valid status
def test_find_by_status_200(status):  
    test_endpoint = "/pets/findByStatus" #checking api filter by pet status 
    params = {"status":status}
    response = api_helpers.get_api_data(test_endpoint,params)
    assert response.status_code == 200
    
    pets=response.json()

    if len(pets) == 0:
      print(f"warning: no pets found with status '{status}'")
    else:
       for pet in pets:
          assert pet["status"] == status
          validate(instance=pet, schema=schemas.pet)

@pytest.mark.parametrize("pet_id", [-1,999999,"invalid"])#test for invalid IDs
def test_find_by_id_404(pet_id):
    test_endpoint = f"/pets/{pet_id}"
    response = api_helpers.get_api_data(test_endpoint)
    assert response.status_code in [404, 400, 405], f"Unexpected status{response.status_code} for pet_id: {pet_id}"    
def test_edge_cases(): #edge case checks 
    response = api_helpers.get_api_data("/pets/findByStatus",{"status":""})
    assert response.status_code in [200,400]

    response = api_helpers.get_api_data("/pets/findByStatus",{"status": "AVAILABLE"}) #case sensttive check
    if response.status_code == 200:
      pets = response.json()
      for pet in pets:
        assert pet["status"].lower()=="available"                                                 