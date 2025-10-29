import http.client
import json
import time
import random
import string
from concurrent.futures import ThreadPoolExecutor
import statistics

# Configuration
BASE_URL = "http://localhost:8000"
NUM_USERS = 10
MESSAGES_PER_USER = 5
CONCURRENT_USERS = 5

def generate_random_string(length=10):
    """Generate a random string for testing."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_test_user():
    """Create a test user and return user data."""
    conn = http.client.HTTPConnection("localhost", 8000)
    
    user_data = {
        "name": f"Load Test User {generate_random_string()}",
        "handle": f"loadtest_{generate_random_string()}"
    }
    
    headers = {'Content-Type': 'application/json'}
    conn.request('POST', '/users/', json.dumps(user_data), headers)
    
    response = conn.getresponse()
    if response.status == 200:
        user = json.loads(response.read().decode())
        conn.close()
        return user
    else:
        conn.close()
        raise Exception(f"Failed to create user: {response.status}")

def create_test_chatroom():
    """Create a test chatroom and return chatroom data."""
    conn = http.client.HTTPConnection("localhost", 8000)
    
    chatroom_data = {
        "name": f"Load Test Room {generate_random_string()}"
    }
    
    headers = {'Content-Type': 'application/json'}
    conn.request('POST', '/chatrooms/', json.dumps(chatroom_data), headers)
    
    response = conn.getresponse()
    if response.status == 200:
        chatroom = json.loads(response.read().decode())
        conn.close()
        return chatroom
    else:
        conn.close()
        raise Exception(f"Failed to create chatroom: {response.status}")

def post_message(user_id, chatroom_id, message_text):
    """Post a message to a chatroom."""
    conn = http.client.HTTPConnection("localhost", 8000)
    
    message_data = {
        "message_text": message_text,
        "user_id": user_id,
        "chatroom_id": chatroom_id
    }
    
    headers = {'Content-Type': 'application/json'}
    conn.request('POST', '/messages/', json.dumps(message_data), headers)
    
    response = conn.getresponse()
    conn.close()
    return response.status == 200

def get_messages(chatroom_id):
    """Get messages from a chatroom."""
    conn = http.client.HTTPConnection("localhost", 8000)
    conn.request('GET', f'/messages/chatroom/{chatroom_id}')
    
    response = conn.getresponse()
    conn.close()
    return response.status == 200

def user_workflow(user_id, chatroom_id):
    """Simulate a user workflow: post messages and read messages."""
    response_times = []
    
    for i in range(MESSAGES_PER_USER):
        # Post a message
        start_time = time.time()
        success = post_message(user_id, chatroom_id, f"Load test message {i} from user {user_id}")
        end_time = time.time()
        
        if success:
            response_times.append(end_time - start_time)
        
        # Small delay between messages
        time.sleep(0.1)
    
    # Read messages
    start_time = time.time()
    success = get_messages(chatroom_id)
    end_time = time.time()
    
    if success:
        response_times.append(end_time - start_time)
    
    return response_times

def run_load_test():
    """Run the load test."""
    print("Starting load test...")
    print(f"Users: {NUM_USERS}, Messages per user: {MESSAGES_PER_USER}")
    print(f"Concurrent users: {CONCURRENT_USERS}")
    
    # Create test data
    print("Creating test users and chatroom...")
    users = []
    for i in range(NUM_USERS):
        try:
            user = create_test_user()
            users.append(user)
        except Exception as e:
            print(f"Failed to create user {i}: {e}")
            return
    
    chatroom = create_test_chatroom()
    print(f"Created {len(users)} users and 1 chatroom")
    
    # Run load test
    print("Running load test...")
    start_time = time.time()
    
    all_response_times = []
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = []
        for user in users:
            future = executor.submit(user_workflow, user['id'], chatroom['id'])
            futures.append(future)
        
        for future in futures:
            try:
                response_times = future.result()
                all_response_times.extend(response_times)
            except Exception as e:
                print(f"User workflow failed: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate statistics
    if all_response_times:
        avg_response_time = statistics.mean(all_response_times)
        median_response_time = statistics.median(all_response_times)
        p95_response_time = statistics.quantiles(all_response_times, n=20)[18]  # 95th percentile
        min_response_time = min(all_response_times)
        max_response_time = max(all_response_times)
        
        print("\n=== Load Test Results ===")
        print(f"Total test time: {total_time:.2f} seconds")
        print(f"Total requests: {len(all_response_times)}")
        print(f"Requests per second: {len(all_response_times) / total_time:.2f}")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Median response time: {median_response_time:.3f}s")
        print(f"95th percentile: {p95_response_time:.3f}s")
        print(f"Min response time: {min_response_time:.3f}s")
        print(f"Max response time: {max_response_time:.3f}s")
    else:
        print("No successful requests recorded")

if __name__ == "__main__":
    run_load_test()
