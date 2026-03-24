class Message:
    def __init__(self, content, result):
        self.content = content
        self.result = result

    def send(self):
        final_format = {"content":self.content, "result": self.result}
        return final_format