class Maximum:
    def __init__(self):
        self.info_headers = {}
        self.value_header = {}

    def append_info_header(self, info_header, info_header_value):
        self.info_headers.update({info_header: info_header_value})
