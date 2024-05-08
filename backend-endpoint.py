from flask import Flask, render_template, request 
  
app = Flask(__name__,template_folder="templates") 
  
@app.route("/") 
def hello(): 
    return render_template('index.html') 
  
@app.route('/process', methods=['POST']) 
def process(): 
    return "it works!"
    # data = request.get_json() # retrieve the data sent from JavaScript 
    # # process the data using Python code 
    # result = data['value'] * 2
    # return jsonify(result=result) # return the result to JavaScript 
  
if __name__ == '__main__': 
    app.run(debug=True)

# from flask import Flask, request, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # This will enable CORS for all routes

# @app.route('/generate-schedule', methods=['GET', 'POST'])
# def generate_schedule():
#     data = request.get_json()
#     major = data['major']
#     semesters = data['semesters']

#     return jsonify({
#         "message": f"Generating schedule for {major} for {semesters} semesters."
#     })

# if __name__ == '__main__':
#     app.run(debug=True)
