COLORS = {
    'default': "\033[0m",
    'red': "\033[31m",
    'green': "\033[32m"
}

def color(text, color_name):
    return COLORS[color_name] + text + COLORS["default"]

def format_result(result):
    return color('OK', 'green') if result else color('FAIL', 'red')
