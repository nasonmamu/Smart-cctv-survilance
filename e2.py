import sys
import subprocess

def fn_get_txt_sysarg():
    """Harvest a single (the only expected) command line argument"""
    try:
        return sys.argv[1]  # str() would be redundant here
    except IndexError:
        error_msg = f'Message from fn_get_txt_sysarg() in Script ({sys.argv[0]}):\n' \
                    '\tThe Script did not receive a command line argument'
        sys.exit(error_msg)

def open_win_explorer_and_select_file(filepath):
    # Harvested from: https://stackoverflow.com/questions/281888/open-explorer-on-a-file
    subprocess.Popen(['explorer', '/select,', filepath])

if __name__ == '__main__':
    filepath = fn_get_txt_sysarg()
    open_win_explorer_and_select_file(filepath)
