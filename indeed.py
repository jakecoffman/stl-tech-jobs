import flask
import requests
import json
from datetime import datetime
import urllib
from operator import itemgetter
try:
    import publisher
except ImportError:
    raise Exception("Apply for a publisher key on indeed.com and put it in publisher.py")

app = flask.Flask(__name__)
db = {}
langs = ['java', 'python', 'c#', 'javascript', 'c++']


def write(data, query):
    open("data/" + query + ".json", 'w').write(json.dumps(data, indent=4))


def query(lang, start=0):
    lang = urllib.quote(lang)
    r = requests.get("http://api.indeed.com/ads/apisearch?publisher={0}&q={1}&l=st%20louis%2C+mo&start={2}&limit=25&co=us&v=2&format=json".format(publisher.key, lang, start))
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
    return flask.render_template("index.html")


@app.route("/charts/lang-by-date")
def lang_by_date():
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
    return flask.render_template("job_lang_by_date.html", data=data)


@app.route("/charts/top-employer")
def top_employer():
    companies = {}
    for lang in langs:
        try:
            results = json.loads(open("data/" + lang + ".json").read())
        except:
            results = get_results(lang)

        for result in results:
            if result['company'] in companies:
                companies[result['company']] += 1
            else:
                companies[result['company']] = 1

    data = sorted(companies.items(), key=itemgetter(1))
    print json.dumps(data[-10:])
    return flask.render_template("top_employer.html", data=data[-10:])

if __name__ == "__main__":
    app.run(debug=True)