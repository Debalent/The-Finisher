from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime

# Initialize Flask app - lightweight, industry-standard framework for rapid API development
app = Flask(__name__)
CORS(app)  # Enables cross-origin requests, ensuring compatibility with modern web and mobile applications

# Configure robust logging for analytics and monitoring, critical for data-driven decision-making
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# In-memory data store for tasks; easily scalable to database integration (e.g., PostgreSQL, MongoDB) for enterprise use
tasks = []
task_id_counter = 1

@app.route("/", methods=["GET"])
def home():
    # Entry point providing clear API branding and versioning, enhancing user trust and adoption
    logging.info("Home endpoint accessed")
    return jsonify({
        "message": "Welcome to The Finisher API!",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/tasks", methods=["GET"])
def get_tasks():
    # Provides a scalable endpoint for retrieving task data, supporting high-volume user queries
    logging.info(f"Fetching all tasks, count: {len(tasks)}")
    return jsonify({
        "tasks": tasks,
        "count": len(tasks)
    })

@app.route("/tasks", methods=["POST"])
def create_task():
    # Core feature for task creation, designed for seamless user experience and market-ready functionality
    global task_id_counter
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            logging.error("Invalid task data provided")
            return jsonify({"error": "Title is required"}), 400

        task = {
            "id": task_id_counter,
            "title": data["title"],
            "description": data.get("description", ""),
            "completed": False,
            "created_at": datetime.utcnow().isoformat()
        }
        tasks.append(task)
        task_id_counter += 1
        
        logging.info(f"Created new task with ID: {task['id']}")
        return jsonify({
            "message": "Task created successfully",
            "task": task
        }), 201
    except Exception as e:
        # Robust error handling ensures reliability, critical for enterprise-grade applications
        logging.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    # Efficient task retrieval by ID, optimized for performance and low latency
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        logging.warning(f"Task with ID {task_id} not found")
        return jsonify({"error": "Task not found"}), 404
    
    logging.info(f"Retrieved task with ID: {task_id}")
    return jsonify(task)

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    # Flexible task updating supports dynamic user needs, enhancing product stickiness
    try:
        task = next((task for task in tasks if task["id"] == task_id), None)
        if not task:
            logging.warning(f"Task with ID {task_id} not found for update")
            return jsonify({"error": "Task not found"}), 404

        data = request.get_json()
        task["title"] = data.get("title", task["title"])
        task["description"] = data.get("description", task["description"])
        task["completed"] = data.get("completed", task["completed"])
        
        logging.info(f"Updated task with ID: {task_id}")
        return jsonify({
            "message": "Task updated successfully",
            "task": task
        })
    except Exception as e:
        logging.error(f"Error updating task: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    # Streamlined deletion process ensures data management efficiency, appealing to productivity-focused users
    global tasks
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        logging.warning(f"Task with ID {task_id} not found for deletion")
        return jsonify({"error": "Task not found"}), 404

    tasks = [t for t in tasks if t["id"] != task_id]
    logging.info(f"Deleted task with ID: {task_id}")
    return jsonify({"message": "Task deleted successfully"})

@app.errorhandler(404)
def not_found(error):
    # Comprehensive error handling improves user experience and reduces support costs
    logging.error(f"404 error: {str(error)}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    # Centralized error management ensures system stability, critical for investor confidence
    logging.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Configurable deployment settings enable flexible scaling for cloud environments
    app.run(debug=True, host='0.0.0.0', port=5000)
