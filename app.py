import json
import os
import pandas as pd
from flask import Flask , request, make_response
from sklearn.preprocessing import Imputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

app = Flask(__name__)

@app.route('/webhook',methods=['POST'])
def webhook():
    req=request.get_json(silent=True,force=True)
    
    response=mvRegression(req)
    res= {"speech": response,"displayText": response,"source": "nWave-estimation-chatbot"}
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def mvRegression(req):
    #Machine Learning Model
    dataset = pd.read_excel("https://github.com/s-gunalan/nWave-Flask-Demo/blob/master/dataset.xlsx?raw=true",skip_header=1)
    #dataset=pd.read_excel("D:/Guna/POCs/ML/nWave_effort/dataset.xlsx",skip_header=1)
    Y=dataset.iloc[:, 13:]
    X=dataset.iloc[:,1:13]
    header=list(X)
    imputer = Imputer()
    dataset = imputer.fit_transform(X)
    lr=LinearRegression()
    model_lr=lr.fit(X,Y)

    #Data Processing
    val=[]
    result=req.get("result")
    contexts=result.get("contexts")
    print(contexts[0])
    parameters=contexts[0].get("parameters")
    for i in header:
        str=parameters.get(i)
        print(str)
        val.append(str)
    ds=pd.DataFrame(val).T
    print(ds)
    op_lrt=lr.predict(ds)
    weightage=round(op_lrt[0][0],2)
    op="Estimated Value for the interface is : %s Do you want to try for another Interface ? (Yes/No) " %(weightage)
    print(op)
    return op




if __name__ == '__main__':
	app.run(use_reloader=True, debug=True)
