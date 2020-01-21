from base.app import App


class Netcat(App):
    _name = "netcat"

    def base_command(self):
        return "nc -l 9556 | nc localhost 9070"
