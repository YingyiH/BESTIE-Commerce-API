import csv
import uuid
import random
import datetime
import time

SELLERS = [
    "SwiftTrade Emporium",
    "VelvetBoutique Finds",
    "QuantumGoods Co.",
    "GoldenHarbor Emporium",
    "UrbanGlow",
    "NovaCraft Retail",
    "ElysianEssentials Sellers"
]

ONSALE = ["true","false"]

DESCRIPTIONS = [
    "Stay connected and monitor your health",
    "Enjoy the soothing scents",
    "Provides the perfect surface",
    "This eco-friendly and reusable bottle",
    "Compact and energy-efficient",
    "Versatile and portable",
    "Crystal-clear sound"
]

CUSTOMERS = [
    "apple123000",
    "emsl02",
    "xxxxx111",
    "lwe_s",
    "hihihihi",
    "yingyi888"
]

LOCATIONS = [
    "Vancouver",
    "Toronto",
    "Montreal",
    "Calgary",
    "Alberta"
]

COMMENTS = [
    "Good",
    "Very good product",
    "It is ok",
    "Not bad",
    "Bought",
    "Great",
    "Do not buy it"
]

# Data to be generated
product_create = []
product_review = []
review_id = []
product_id = []

for _ in range(1000):
    _uuid = str(uuid.uuid4())
    product_id.append(_uuid)
    row = {
        "product_id": _uuid,
        "seller": random.choice(SELLERS),
        "price": random.randint(16, 999),
        "onsale": random.choice(ONSALE),
        "description":random.choice(DESCRIPTIONS)
    }
    product_create.append(row)

for _ in range(1000):
    _uuid = str(uuid.uuid4())
    row = {
        "review_id": _uuid,
        "product_id": _uuid,
        "customer": random.choice(CUSTOMERS),
        "location": random.choice(LOCATIONS),
        "rating": random.randint(0,10),
        "comment": random.choice(COMMENTS)
    }
    product_review.append(row)

# CSV file writing


def write_csf(data, file_name):
    csv_filename = f"{file_name}.csv"
    csv_columns = data[0].keys()

    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"Mock data has been written to {csv_filename}")


write_csf(product_create, "product_data")
write_csf(product_review, "comment_data")
