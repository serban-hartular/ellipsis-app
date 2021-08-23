from flask import Flask, send_from_directory
from flask import request
import json
import urllib

NLPCUBE_ENABLE = False

if NLPCUBE_ENABLE:
    import get_nlpcube_parse
import get_racai_parse

app = Flask(__name__)

# Path for our main Svelte page
@app.route("/")
def test():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)

@app.route("/static/")
def static_dir_index():
    return send_from_directory("static", "index.html")


@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.route("/parse", methods=['POST'])
def parse_text():
    return_obj = {'tree': dict(), 'error_msg': ''}
    obj = None
    try: # get json obj
        obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    try: # get members
        text = obj['text']
        lang = obj['lang'] if 'lang' in obj and obj['lang'] else 'ro'
        parser = obj['parser'] if 'parser' in obj and obj['parser'] else 'nlpcube'
    except Exception as e:
        return_obj['error_msg'] = 'Error: Request lacks property ' + str(e)
        return return_obj
    if parser == 'racai':
        parse_obj = get_racai_parse.get_racai_parse(text, lang)
        return_obj['tree'] = parse_obj
    else:
        if lang == 'en':
            host = 'http://localhost:5008' # english lang parser
        else:
            host = 'http://localhost:5009' # romanian lang parser
        r = urllib.request.urlopen(host, json.dumps({'text':text}).encode('utf8'))
        html = r.read()
        parse = html.decode('utf-8')
        return_obj = json.loads(parse)
        print(return_obj)
    
    return json.dumps(return_obj)

import database

@app.route("/store", methods=['POST'])
def store_to_db():
    return_obj = {'error_msg': ''}
    obj = None
    try: # get json obj
        obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return json.dumps(return_obj)
    try: # get members
        conllu = obj['conllu']
        lang = obj['lang']
        comment = obj['comment']
        sentence_src = obj['sentence_src']
    except Exception as e:
        return json.dumps({'error_msg': 'Error: Request lacks property ' + str(e)})

    filename = r'sentences_ro1.db'
    conn = database.create_connection(filename)
    if not conn:
        return {'error_msg': 'Error connecting to database'}
    id = database.insert_sentence(conn, conllu, '', '', request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
                                  1, 1, '', comment, sentence_src)
    conn.close()
    # print(id)
    return json.dumps(return_obj)


if __name__ == "__main__":
    app.run(debug=True, port='5000') # need to add host option
