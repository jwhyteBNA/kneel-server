import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from views import get_all_metals, get_all_orders, get_all_sizes, get_all_styles, get_all_jewelry
from views import get_single_metal, get_single_order, get_single_size, get_single_style
from views import get_single_jewelry, create_order
from views import delete_order, update_metal

method_mapper = { }

class HandleRequests(BaseHTTPRequestHandler):
    """Controls the functionality of any GET, PUT, POST, DELETE requests to the server
    """

    def get_all_or_single(self, resource, id):
        """DRY method for all or single."""
        if id is not None:
            response = method_mapper[resource]["single"](id)

            if response is not None:
                self._set_headers(200)
            else:
                self._set_headers(404)
                response = ''
        else:
            self._set_headers(200)
            response = method_mapper[resource]["all"]()

        return response

    # def do_GET(self):
    # response = None
    # (resource, id) = self.parse_url(self.path)
    # response = self.get_all_or_single(resource, id)
    # self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        """Handles GET requests to the server """
        response = {}
        (resource, id) = self.parse_url(self.path)

        if resource == "metals":
            if id is not None:
                response = get_single_metal(id)
                if response is not None:
                    self._set_headers(200)
                else:
                    self._set_headers(404)
                    response = { "message": "That metal is not currently in stock for jewelry." }
            else:
                self._set_headers(200)
                response = get_all_metals()

        if resource == "sizes":
            if id is not None:
                response = get_single_size(id)
                if response is not None:
                    self._set_headers(200)
                else:
                    self._set_headers(404)
                    response = { "message": "That size is not currently in stock for jewelry." }
            else:
                self._set_headers(200)
                response = get_all_sizes()

        if resource == "styles":
            if id is not None:
                response = get_single_style(id)
                if response is not None:
                    self._set_headers(200)
                else:
                    self._set_headers(404)
                    response = { "message": "That style is not currently in stock for jewelry." }
            else:
                self._set_headers(200)
                response = get_all_styles()

        if resource == "jewelry":
            if id is not None:
                response = get_single_jewelry(id)
                if response is not None:
                    self._set_headers(200)
                else:
                    self._set_headers(404)
                    response = { "message": "That jewelry type is out of stock." }
            else:
                self._set_headers(200)
                response = get_all_jewelry()

        if resource == "orders":
            if id is not None:
                response = get_single_order(id)
                if response is not None:
                    self._set_headers(200)
                else:
                    self._set_headers(404)
                    response = { "message": "That order was never placed, or was cancelled." }
            else:
                self._set_headers(200)
                response = get_all_orders()

# Original path before creating functions for single objects
        # if self.path == "/metals":
        #     response = get_all_metals()

        # elif self.path == "/styles":
        #     response = get_all_styles()

        # elif self.path == "/sizes":
        #     response = get_all_sizes()

        # elif self.path == "/orders":
        #     response = get_all_orders()
        # else:
        #     response = []

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handles POST requests to the server """
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)
        (resource, _) = self.parse_url(self.path)

        #Initialize new order
        new_order = None
        if resource == "orders":
            if "metal_id" in post_body and "size_id" in post_body and "style_id" in post_body and "jewelry_id" in post_body:
                self._set_headers(201)
                new_order = create_order(post_body)
            else:
                self._set_headers(400)
                new_order = {"message": f'{"Metal is required" if "metalId" not in post_body else ""} {"size is required" if "sizeId" not in post_body else ""} {"style is required" if "styleId" not in post_body else ""}{"jewelry type is required" if "jewelryId" not in post_body else ""}'}
            self.wfile.write(json.dumps(new_order).encode())

    def do_DELETE(self):
        """To Delete Items."""
        # Set a 204 response code

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        if resource == "orders":
            self._set_headers(204)
            delete_order(id)
            self.wfile.write("".encode())

        # Do not allow delete of an order from the list
        # if resource == "orders":
        #     self._set_headers(405)
        #     delete_order = { "message": "To delete order, contact the company directly." }
        #     self.wfile.write(json.dumps(delete_order).encode())

    def do_PUT(self):
        """Handles PUT requests to the server"""
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)
        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        success = False

        # if resource == "orders":
        #     update_order(id, post_body)
        # if resource == "orders":
        #     self._set_headers(405)
        #     update_order = { "message": "Order is now in production and cannot be updated." }
        #     self.wfile.write(json.dumps(update_order).encode())
        if resource == "metals":
            success = update_metal(id, post_body)

        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)

        self.wfile.write("".encode())



        # Encode the new order and send in response
        self.wfile.write("".encode())

    def _set_headers(self, status):
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response

        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        """Sets the options headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                        'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers',
                        'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    def parse_url(self, path):
        """parsing"""
        # Just like splitting a string in JavaScript. If the
        # path is "/metals/1", the resulting list will
        # have "" at index 0, "metals" at index 1, and "1"
        # at index 2.
        path_params = path.split("/")
        resource = path_params[1]
        id = None

        # Try to get the item at index 2
        try:
            # Convert the string "1" to the integer 1
            # This is the new parseInt()
            id = int(path_params[2])
        except IndexError:
            pass  # No route parameter exists: /metals
        except ValueError:
            pass  # Request had trailing slash: /metals/

        return (resource, id)  # This is a tuple

#Starting point of this application.
def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()

if __name__ == "__main__":
    main()
