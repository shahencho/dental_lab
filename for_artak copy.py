import requests

token = "patn2i70wkWoPc6oJ.47cc30c3d1aa2a98408c72984007832ce06bfb6e20d312712b1b24d28cf12c03"
base_id = "app0gf8ECLPKzB9uN"
table_name = "Orders"  # replace this

url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

headers = {"Authorization": f"Bearer {token}"}
res = requests.get(url, headers=headers)



print(res.status_code)
print(res.json())
