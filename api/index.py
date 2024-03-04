from http.server import BaseHTTPRequestHandler
import json
import socketserver
from http import HTTPStatus
from urllib.parse import parse_qs
import cgi
import ifcopenshell
import ifcopenshell.util.element
import os
cwd = "/root/ifc-viz/vercel-test/api"

class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        # respond with a simple html page with a form that posts a file to the same url
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(open(cwd + '/index.html', 'r').read().encode('utf-8'))
        return
    
    # receive a IFC file in a post request and return a json with the IFC file name
    def do_POST(self):

        # parse as multipart/form-data
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE':self.headers['Content-Type'],
                    })
        
        # check if the file is in the form
        if "file" not in form:
            self.send_response(400)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "No file found"}).encode('utf-8'))
            return
        
        # get the file from the form
        fileitem = form["file"]
        
        # check if the file is in the form
        if fileitem.filename == '':
            self.send_response(400)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "No file found"}).encode('utf-8'))
            return
        
        # read the file
        post_data = fileitem.file.read()

        # write the content to a file
        filename = "ifc_file.ifc"
        with open(filename, "wb") as f:
            f.write(post_data)
        try:    
            my_list = process_file(filename)
        except Exception as e:
            ef = open("errfile", "a") 
            ef.write(repr(e) + "\n")
            msg = "error: " + str(repr(e))
            
            self.send_response(500)
            self.send_header('Content-type','text/*')
            self.end_headers()
            self.wfile.write(str(msg).encode('utf-8'))
            return
        # respond with json {"message": "Hello World!"}
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

        # json.stringify({"my_list": my_list})
        self.wfile.write(json.dumps({"my_list": my_list}).encode('utf-8'))

        return

        

def process_file(file_name):
    model = ifcopenshell.open(file_name)

    # Get model name
    model_name = file_name.split("/")[-1]
    # Make the name cleaner
    # model_name = model_name.split(".")[0].replace("_", " ").replace("-", " ").title()
    # print(model_name)
    json_dict = {model_name: {"floors": []}}

    floors = [floor for floor in model.by_type('IfcSlab') if
              ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]
    if len(floors) == 0:
        return "No floors found!<br>"

    result = f"Amount of floor type objects: {len(floors)}<br><br>"

    for floor in floors:
        # Get the right properties
        properties = ifcopenshell.util.element.get_psets(floor)
        base_properties = properties["BaseQuantities"]

        json_dict[model_name]["floors"].append({floor.Name: base_properties['GrossArea']})
    #         result += f"Object name: {floor.Name}<br>"
    #         result += f"&emsp;&emsp;Area: {base_properties['GrossArea']} m^2<br>"
    final_json = json.dumps(json_dict)
    print(final_json)
    return json_dict[model_name]["floors"]


if __name__ == '__main__':
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        print("serving at port", 8080)
        httpd.serve_forever()
        
    # start the server
    # from http.server import HTTPServer
    # server = HTTPServer(('', 8080), handler)
    # server.serve_forever()
