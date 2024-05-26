from flask import Flask, render_template, request, jsonify
import pandas as pd
from extract import readexcel
from apscheduler.schedulers.background import BackgroundScheduler
from main import process_data_and_save_to_csv

app = Flask(__name__)
 
items = []
department = []
df1 = None
 
@app.route('/')
def index():
    global items, department
   
    return render_template('index.html')
 
 
def extractdata():
    print("Executing scheduled task")
    try:
        process_data_and_save_to_csv()
        # print("JavaScript function executed successfully:")
    except Exception as e:
        print("Error executing Data Extraction:", e)
 
def start_scheduler():
    print("In scheduler")
    scheduler = BackgroundScheduler()
    print("Scheduler is Active")
    scheduler.add_job(extractdata, 'interval', minutes=10)
    scheduler.start()
 
@app.route('/sendData', methods=['POST'])
def receive_data():
    global df1, items, department
    items, department, df1 = readexcel()
    columns1 = ['Bid Number', 'RA Number', 'Items', 'Quantity', 'Department', 'Start Date', 'End Date']
    df2 = pd.DataFrame(columns=columns1)
    # # temp = items + department
    # for i in items:
    #     # filtered_df = df1[df1.apply(lambda row: row.astype(str).str.contains(i, case=False).any(), axis=1)]
    #     filtered_df = df1[df1['Items'].str.contains(i, case=False, na=False)]
    #     df2 = pd.concat([df2, filtered_df], ignore_index=True)
    # for i in department:
    #     # filtered_df = df1[df1.apply(lambda row: row.astype(str).str.contains(i, case=False).any(), axis=1)]
    #     filtered_df = df1[df1['Department'].str.contains(i, case=False, na=False)]
    #     df2 = pd.concat([df2, filtered_df], ignore_index=True)
    df2 = pd.concat([df2,df1],ignore_index=True)
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
#    --------------------------------------------
    filtered_df_items = pd.DataFrame(columns=columns1)
    filtered_df_items = df1[df1['Items'].str.contains('|'.join(selected_items), case=False, na=False)]
    filtered_df = filtered_df_items[filtered_df_items['Department'].str.contains('|'.join(selected_departments), case=False, na=False)]
    json_df = filtered_df.to_json(orient='records')
# ----------------------------------------

    # if not temp:
    #     df3 = pd.DataFrame(columns=columns1)
    #     df3 = pd.concat([df3, df1], ignore_index=True)
    #     json_df = df3.to_json(orient='records')
    # else:
    #     for i in temp:
    #         filtered_df = df1[df1.apply(lambda row: row.astype(str).str.contains(i, case=False).any(), axis=1)]
    #         df2 = pd.concat([df2, filtered_df], ignore_index=True)
    #     json_df = df2.to_json(orient='records')
 
    return jsonify({'dataframe': json_df})
 
 
@app.route('/submit_form', methods=['POST'])
def submit_form():
    global items, department,df1
    item_new = None
    department_new = None
    data = request.get_json()
    if data.get('item') is not None:
        item_new = data.get('item')
        item_new = item_new.split("\n")
        for i in item_new:
            items.append(i)
       
    if data.get('department') is not None:
        department_new = data.get('department')
        department_new = department_new.split("\n")
        for i in department_new:
            department.append(i)
   
    # Process item and department
    items = list(filter(lambda x: x != '', items))
    department = list(filter(lambda x: x != '', department))
   
    print(items)
    print(department)
 
    return jsonify({'items': items, 'department': department})
 
if __name__ == '__main__':
    # start_scheduler()
    app.run(host='0.0.0.0', debug=True)