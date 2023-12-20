from flask import Flask, render_template, request
import AlphaBot as ab
from time import sleep

app = Flask(__name__)

susina = ab.AlphaBot()
moves = {'avanti': susina.forward, 'indietro': susina.backward, 'destra': susina.right, 'sinistra': susina.left}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        moves[request.form.get('move')]()
        sleep(1)
        susina.stop()
    return render_template('index.html')

app.run(debug=True, host='0.0.0.0')