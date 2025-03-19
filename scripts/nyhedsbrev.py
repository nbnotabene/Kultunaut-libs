import requests

url = "https://bulk.api.mailtrap.io/api/send"

payload = "{\"from\":{\"email\":\"hello@svanekebio.dk\",\"name\":\"Mailtrap Test\"},\"to\":[{\"email\":\"bio@svaneke.net\"}],\"template_uuid\":\"9e765a0b-8d54-4862-a296-e6d5b60b31ef\",\"template_variables\":{\"user_email\":\"Test_User_email\",\"pass_reset_link\":\"Test_Pass_reset_link\"}}"
headers = {
  "Authorization": "Bearer eb11a245f6ee4ed5392aebfbfe4ee77c",
  "Content-Type": "application/json"
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)