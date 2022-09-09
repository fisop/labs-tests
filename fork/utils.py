COLORS = {
    'default': "\033[0m",
    'red': "\033[31m",
    'green': "\033[32m"
}

VALGRIND_COMMAND = ['valgrind', '--track-fds=yes', '--leak-check=full', '--show-leak-kinds=all']

def color(text, color_name):
    return COLORS[color_name] + text + COLORS["default"]

def format_result(result):
    return color('OK', 'green') if result else color('FAIL', 'red')

def are_equal(expected, current):
    # ^ symmetric difference operator
    diff = expected ^ current

    return len(diff) == 0
