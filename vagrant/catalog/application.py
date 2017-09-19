from flask import Flask
from flask import render_template 
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html', body_content="fart")


#return app.send_static_file('index.html')
#return "Hello World!"

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)