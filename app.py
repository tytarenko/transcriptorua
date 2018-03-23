from flask import Flask, Response, request, render_template, abort, jsonify
from transcriptorua import get_transcription
from collections import deque
import json
import os

path = os.path.dirname(os.path.abspath(__file__))
datafile = '{}/data.json'.format(path)


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    with open(datafile) as fp:
        data = json.load(fp)
    d = deque(data, maxlen=5)
    params = {'last_queries': list(d)[::-1]}
    if request.method == 'POST':
        word = request.form.get("word")
        if word:
            try:
                transcription = get_transcription(word)
                d.append((word, transcription))
                params.update({'transcription': transcription, 'word': word})
                with open(datafile, 'w') as fp:
                    json.dump(list(d), fp)
            except ValueError as e:
                params.update({'error': 'Введене слова містить символи які відсутні в українській абетці'})

    return render_template('index.html', **params)


if __name__ == '__main__':
    app.run()
