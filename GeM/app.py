from flask import Flask, render_template, request, jsonify
import pandas as pd
from extract import startfun

app = Flask(__name__)

items = []
department = []
df1 = None

@app.route('/')
def index():
    global items, department
    return render_template('index.html')

@app.route('/sendData', methods=['POST'])
def receive_data():
    global df1, items, department
    items, department, df1 = startfun()
    columns1 = ['Bid Number', 'RA Number', 'Items', 'Quantity', 'Department', 'Start Date', 'End Date']
    df2 = pd.DataFrame(columns=columns1)
    temp = items + department
    for i in temp:
        filtered_df = df1[df1.apply(lambda row: row.astype(str).str.contains(i, case=False).any(), axis=1)]
        df2 = pd.concat([df2, filtered_df], ignore_index=True)

    json_df = df2.to_json(orient='records')  
    return jsonify({'items': items, 'department': department, 'dataframe': json_df})

@app.route('/refreshData', methods=['POST'])
def refresh_data():
    global df1
    data = request.json
    selected_items = data.get('selectedItems')
    selected_departments = data.get('selectedDepartments')
    columns1 = ['Bid Number', 'RA Number', 'Items', 'Quantity', 'Department', 'Start Date', 'End Date']
    df2 = pd.DataFrame(columns=columns1)
    temp = selected_items + selected_departments
    for i in temp:
        filtered_df = df1[df1.apply(lambda row: row.astype(str).str.contains(i, case=False).any(), axis=1)]
        df2 = pd.concat([df2, filtered_df], ignore_index=True)

    json_df = df2.to_json(orient='records') 
    return jsonify({'dataframe': json_df})

@app.route('/submit_form', methods=['POST'])
def submit_form():
    global items, department,df1
    data = request.get_json()
    item_new = data.get('item')
    department_new = data.get('department')
    item_new = item_new.split("\n")
    department_new = department_new.split("\n")
    # Process item and department
    for i in item_new: 
        items.append(i)
    for i in department_new:
        department.append(i)
    print(items)
    print(department)

    return jsonify({'items': items, 'department': department})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
