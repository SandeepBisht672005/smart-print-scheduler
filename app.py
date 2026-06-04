from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import heapq
import time
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Print queue implemented as a priority queue
# Format: (priority_level, arrival_timestamp, job_id, name, file_name)
print_queue = []
job_counter = 0
job_history = []  # To store completed print jobs

# Priority levels mapping
PRIORITY_LEVELS = {
    "CEO": 1,
    "Director": 2,
    "Manager": 3,
    "Team Lead": 4,
    "Senior Employee": 5,
    "Regular Employee": 6,
    "Intern": 7
}

# Simulate printing process
is_printing = False
current_job = None

@app.route('/')
def index():
    global print_queue
    priority_levels = sorted(PRIORITY_LEVELS.items(), key=lambda x: x[1])
    return render_template('index.html', 
                          queue=sorted(print_queue), 
                          is_printing=is_printing,
                          current_job=current_job,
                          priority_levels=priority_levels,
                          job_history=job_history)

@app.route('/submit', methods=['POST'])
def submit_job():
    global job_counter, print_queue
    
    name = request.form.get('name', '').strip()
    position = request.form.get('position', '').strip()
    file_name = request.form.get('file_name', '').strip()
    
    if not name or not position or not file_name:
        flash('All fields are required!', 'error')
        return redirect(url_for('index'))
    
    if position not in PRIORITY_LEVELS:
        flash(f'Invalid position. Please select from the available options.', 'error')
        return redirect(url_for('index'))
    
    # Get priority level (lower number = higher priority)
    priority = PRIORITY_LEVELS[position]
    
    # Use arrival timestamp for tie-breaking within same priority
    arrival_time = time.time()
    
    # Increment job counter
    job_counter += 1
    
    # Add to priority queue
    heapq.heappush(print_queue, (priority, arrival_time, job_counter, name, file_name, position))
    
    flash(f'Print job submitted successfully! Job ID: {job_counter}', 'success')
    
    # Start the printing process if not already running
    if not is_printing:
        start_printing()
    
    return redirect(url_for('index'))

@app.route('/start_printing')
def start_printing():
    global is_printing, current_job, print_queue
    
    if is_printing:
        return jsonify({"status": "already_printing"})
    
    if not print_queue:
        return jsonify({"status": "no_jobs"})
    
    is_printing = True
    current_job = heapq.heappop(print_queue)
    
    # Schedule the job to finish after some time (simulating printing)
    # In a real app, this would be handled differently
    return jsonify({"status": "started", "job": current_job})

@app.route('/finish_job')
def finish_job():
    global is_printing, current_job, job_history
    
    if not is_printing:
        return jsonify({"status": "not_printing"})
    
    # Add to job history with completion time
    job_with_completion = current_job + (datetime.now().strftime("%H:%M:%S"),)
    job_history.insert(0, job_with_completion)  # Add to beginning for recent-first
    
    # Keep history limited to last 10 jobs
    if len(job_history) > 10:
        job_history = job_history[:10]
    
    # Reset current job
    current_job = None
    is_printing = False
    
    # Start next job if available
    if print_queue:
        start_printing()
    
    return jsonify({"status": "completed", "next_job": current_job, "queue_length": len(print_queue)})

@app.route('/queue_status')
def queue_status():
    return jsonify({
        "is_printing": is_printing,
        "current_job": current_job,
        "queue_length": len(print_queue),
        "queue": sorted(print_queue)
    })

if __name__ == '__main__':
    app.run(debug=True)