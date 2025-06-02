import csv
import json
import random
import string

def generate_password(length=12):
    """Generate a random password with mix of characters"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?"
    return ''.join(random.choice(chars) for _ in range(length))

def csv_to_json(csv_file, json_file):
    # List to hold all team data
    teams = []
    
    # Read CSV file
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Skip the header row
        headers = next(reader)
        
        # Process each row (team)
        for row in reader:
            if not row[0]:  # Skip empty rows
                continue
                
            team_name = row[0]
            team_password = generate_password()
            
            # Add teambracket based on Team Leader's Class
            tl_class = row[4]  # TL Class
            if len(tl_class) == 6:
                team_bracket = 1
            elif len(tl_class) == 2:
                team_bracket = 2
            elif len(tl_class) == 3:
                team_bracket = 3
            else:
                raise ValueError(f"Team Leader Class '{tl_class}' for team '{team_name}' must be 2, 3, or 6 characters long")
            
            # Initialize users list
            users = []
            
            # Add team leader if present
            if row[1] and row[3]:  # Name and email exist
                users.append([
                    row[1],  # TL Full Name
                    row[3],  # TL School Email
                    generate_password()
                ])
            
            # Add team member 1 if present
            if row[7] and row[9]:  # Name and email exist
                users.append([
                    row[7],  # TM1 Full Name
                    row[9],  # TM1 School Email
                    generate_password()
                ])
            
            # Add team member 2 if present
            if row[13] and row[15]:  # Name and email exist
                users.append([
                    row[13],  # TM2 Full Name
                    row[15],  # TM2 School Email
                    generate_password()
                ])
            
            # Add team member 3 if present
            if row[19] and row[21]:  # Name and email exist
                users.append([
                    row[19],  # TM3 Full Name
                    row[21],  # TM3 School Email
                    generate_password()
                ])
            
            # Only add teams with at least one user
            if users:
                teams.append({
                    "team": team_name,
                    "teampwd": team_password,
                    "teambracket": team_bracket,  # Add the new field
                    "users": users
                })
    
    # Write to JSON file
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(teams, file, indent=4)
    
    print(f"Successfully converted {len(teams)} teams to {json_file}")

if __name__ == "__main__":
    csv_to_json("data.csv", "data.json")