# Wrapper class to wrap data from our tool. This is for non-graph data only
class DataContainer:
    def __init__(self):
        self.info_headers = {}
        self.value_headers = {}

    def append_info_header(self, info_header, info_header_value):
        self.info_headers.update({info_header: info_header_value})

    def append_value_header(self, value_header, value):
        self.value_headers.update({value_header: value})