import time, requests, json

start = time.time()
print('Sending request to /api/query...')
resp = requests.post('http://127.0.0.1:8000/api/query', json={'query': 'What is the capital of France?'})

try:
    data = resp.json()
    total_time = time.time() - start
    print(f'Total time: {total_time:.2f}s')
    
    if 'execution_steps' in data:
        for step in data['execution_steps']:
            print(f"{step['label']}: {step.get('elapsedMs', 0) / 1000:.2f}s")
    else:
        print('No execution steps found.', data.keys())
except Exception as e:
    print('Failed to parse response:', resp.text[:500])
