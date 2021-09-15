from flask import Flask, Response, request, jsonify 
from flask_restful import Resource, Api, reqparse
from backorder_final_pipeline import final_fun_2
import pandas as pd

import flask
app = Flask(__name__)
api = Api(app)


@app.route('/')
def form():
    return flask.render_template('index.html')



@app.route('/final_fun', methods=["POST"])
def predict():
    f = request.files['data_file']
    if not f:
        return "No file"
    
    df_test = pd.read_csv(f)
    output = final_fun_2(df_test)
    return jsonify({'Actual value' : pd.Series(output[0]).to_json(orient='values'), 'Predicted value' : pd.Series(output[1]).to_json(orient='values')})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)





