import json

# Mapping (right side → left side)
mapping = {
    "Consumer Protection domain": "Consumer_Protection_Laws",
    "Criminal domain": "Criminal_Laws_and_IPC",
    "Cyber crime domain": "Cyber_Laws_and_IT_Act",
    "Properties & land domain": "Property_and_Land_Laws",
    "Labour & Employement domain": "Employment_and_Labor_Laws",
    "Motor Vehicle domain": "Motor_Vehicle_and_Traffic_Laws",
    "Women protection domain": "Family_and_Marriage_Laws",
    "Civil Disputes domain": "Intellectual_Property_Laws",
    "Government Docs & Identity Rights": "Environmental_Laws"  # choose one if duplicate
}

# Load JSON file
with open("merged_legal_docs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Update stage2_category
for item in data:
    domain = item.get("stage2_category")
    if domain in mapping:
        item["stage2_category"] = mapping[domain]

# Save updated JSON
with open("data_updated.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("JSON updated successfully!")