from flask import Flask, send_from_directory
from flask import request
import json
import get_nlpcube_parse  
import sys
from cube.api import Cube

app = Flask(__name__)

cube = None
OLD_API = True

@app.route("/", methods=['POST'])
def parse_text():
    # print(request.get_data())
    try: # get json obj
        request_obj = json.loads(str(request.get_data(),'utf8')) #request.get_json()
    except Exception as e:
        return {'tree': [], 'error_msg': str(e)}
    text = request_obj['text']
    return_obj = {'tree': get_nlpcube_parse.text_to_treelist(text, cube, OLD_API), 'error_msg':''}
    return json.dumps(return_obj)

if __name__ == "__main__":
    args = {'port':'5009', 'lang':'ro', 'api':'old'} # defaults
    for arg in sys.argv[1:]:
        k,v = arg.split('=',1)
        if k in args:
            args[k] = v
    print(args)
    OLD_API = (args['api'] == 'old')
    cube = Cube(verbose=True)    
    cube.load(args['lang'])
    app.run(debug=True, port=args['port'], use_reloader=False)