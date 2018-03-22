import json
import os
import requests
import pickle
import pandas as pd
from cloudant import Cloudant
from flask import Flask , request, make_response , render_template, session
from sklearn.preprocessing import Imputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.decomposition import PCA
user= "199e9aa2-712e-49c8-968f-f1c1baf086f0-bluemix"
password= "6c660ff03ea2090d0aa5fe426c7b7d64bc0a07b490053bad52222cca4315e59a"
host= "199e9aa2-712e-49c8-968f-f1c1baf086f0-bluemix.cloudant.com"
url = 'https://' + host
client = Cloudant(user, password, url=url, connect=True)    
app = Flask(__name__)
app.config['SECRET_KEY']="QWERTYUIOPASDFGHJKLZXCVBNM"

@app.route('/')
def homepage():
    return render_template('chatbotPage.html')

@app.route('/webhook',methods=['POST'])
def webhook():
    url="https://nwave-ideabot-flask-webhook-p.herokuapp.com/storedata"
    global output
    output={}
    try:
        req=request.get_json(silent=True,force=True)
        sessionId=req.get("sessionId")
        weightage=intRegression(req)
        if sessionId in output:
            output[sessionId].append(weightage)
        else:
            output[sessionId]=[weightage]
        print(output)
        op={sessionId:weightage}
        if client:
            print(list(map(lambda doc: doc['name'], db)))
            db.create_document(op)
        else:
            print(list(map(lambda doc: doc['name'], db)))
            print("document not created")
        #send_data=requests.post(url,data={'key':weightage,'sessionId':sessionId})
        session['Id']=sessionId
        
        response="Estimated Value for the interface is : %s Person Days. Do you need estimation for another interface ? (Yes/No) " %(weightage)
    except:
        response="Sorry Bot has faced an issue! Please try after sometime!"
    
    res= {"speech": response,"displayText": response,"source": "nWave-estimation-chatbot"}
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
   
def intRegression(req):
    #Machine Learning Model
    dataset = pd.read_excel("https://github.com/s-gunalan/nWave-Flask-Demo/blob/master/dataset.xlsx?raw=true",skip_header=1)
    #dataset=pd.read_excel("D:/Guna/POCs/ML/nWave_effort/dataset_integration.xlsx",skip_header=1)
    Y=dataset.iloc[:, 13:]
    X=dataset.iloc[:,1:13]
    header=list(X)
    imputer = Imputer()
    dataset = imputer.fit_transform(X)
    lr=LinearRegression()
    model_int=lr.fit(X,Y)

    #Data Processing
    val=[]
    result=req.get("result")
    contexts=result.get("contexts")
    print(contexts[0])
    parameters=contexts[0].get("parameters")
    for i in header:
        str=parameters.get(i)
        print("%s %s " %(i,str))
        val.append(str)
    ds=pd.DataFrame(val).T
    print(ds)

    #Prediction
    op_lrt=lr.predict(ds)
    op=round(op_lrt[0][0],2)
    print(op)
    return op

@app.route('/storedata',methods=['POST'])
def storedata():
    sid=request.get('sessionId')
    weight=request.get('key')
    print ("%s :  %s" %(sid,weight))
    print (request.data)
    return ""

@app.route('/getop')
def getop():
    try:
        df=pd.read_pickle('output.json')
        print(df)
        Id=session['Id']
        session.pop('Id', None)
        print(Id)
        return render_template('output.html',Id=Id)
    except:
        return render_template('nop.html')
    


port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
       	app.run(host='0.0.0.0', port=int(port), use_reloader=True, debug=True)
