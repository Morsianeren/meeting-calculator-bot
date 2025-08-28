def extract_initials(email):
    if '@' not in email:
        raise Exception('Invalid email')
    return email.split('@')[0]

def calculate_meeting_cost(participants, duration_hours, initials_roles, role_costs):
    total = 0
    for email in participants:
        initials = extract_initials(email)
        role = initials_roles.get(initials)
        rate = role_costs.get(role, 0) if role else 0
        total += rate * duration_hours
    return total

def calculate_meeting_cost_with_warnings(participants, duration_hours, initials_roles, role_costs):
    warnings = []
    total = 0
    for email in participants:
        initials = extract_initials(email)
        role = initials_roles.get(initials)
        if not role:
            warnings.append(initials)
            role = 'undefined'
        rate = role_costs.get(role, 0)
        total += rate * duration_hours
    return total, warnings
