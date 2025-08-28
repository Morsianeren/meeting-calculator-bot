def aggregate_feedback(feedback_list):
    if not isinstance(feedback_list, list):
        raise Exception('Invalid feedback data')
        
    # Check if any item in the list is None or not a dict
    if any(item is None or not isinstance(item, dict) for item in feedback_list):
        raise Exception('Invalid feedback data')
        
    useful_count = sum(1 for f in feedback_list if f.get('useful'))
    improvements = [f['improvements'] for f in feedback_list if f.get('improvements')]
    return {'useful_count': useful_count, 'improvements': improvements}
