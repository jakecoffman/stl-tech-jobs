import flask
import requests
import json
from datetime import datetime
import urllib

app = flask.Flask(__name__)
db = {}
langs = ['java', 'python', 'c#', 'javascript', 'c++']


def write(data, query):
    open("data/" + query + ".json", 'w').write(json.dumps(data, indent=4))


def query(lang, start=0):
    lang = urllib.quote(lang)
    r = requests.get("http://api.indeed.com/ads/apisearch?publisher=635112550631030&q={0}&l=st%20louis%2C+mo&start={1}&limit=25&co=us&v=2&format=json".format(lang, start))
    return r.json()


def get_results(lang):
    d = query(lang, 0)
    total = d['totalResults']
    results = d['results']
    limit = 25
    i = limit
    while i < total:
        d = query(lang, i)
        results += d['results']
        i += limit
    # Convert dates to iso format for easier javascript consumption
    for i, result in enumerate(results):
        results[i]['date'] = datetime.strptime(result['date'], "%a, %d %b %Y %H:%M:%S %Z").isoformat()
    write(results, lang)
    return results


@app.route("/")
def index():
    data = {}
    for lang in langs:
        data[lang] = []
        try:
            results = json.loads(open("data/" + lang + ".json").read())
        except:
            results = get_results(lang)

        inner = {}

        for result in results:
            d = datetime.strptime(result['date'], '%Y-%m-%dT%H:%M:%S')
            d = d.strftime("%Y,%m,%d")
            if d in inner:
                inner[d] += 1
            else:
                inner[d] = 1

        data[lang] = inner.items()
        data[lang].sort()
    print json.dumps(data, indent=4)
    return flask.render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)