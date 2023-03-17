# step 1
from flask import Flask,request,render_template
import re 
# step 2
app = Flask(__name__)

#step 3a
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/result',methods=['POST'])
def result():
    string = request.form.get('string')
    regex = request.form.get('regex')
    match = re.findall(regex,string)
    match1=len(match)
    return render_template('result.html',match = match,match1=match1)


# step 4
if __name__ == "__main__":
    app.run(debug=True)

