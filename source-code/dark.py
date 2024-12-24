import os
import sys

try:
    from dark_lang_code.dark import CommandProcessor
    from dark_lang_code.classes import VariableStore, BlockStore

    if __name__ == "__main__":
        store = VariableStore()
        block_store = BlockStore()
        command_processor = CommandProcessor(store, block_store)

        args = sys.argv

        if len(args) < 2:
            print("No file scripts")
            sys.exit(1)

        file_name = args[1]
        debug = False

        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line == '<-#-> dark debug start':
                        print(f"\033[38;2;0;0;0mstart - debug mode\033[0m")
                        debug = True
                        continue
                    if line == '<-#-> dark debug stop':
                        print(f"\033[38;2;0;0;0mstop - debug mode\033[0m")
                        debug = False
                        continue
                    if line:
                        if debug:
                            print(f"\033[38;2;255;255;0m{line}\033[0m"+' -> ', end='')
                        result = command_processor.execute(line)
                        if result is None and debug:
                            print('There is no output')
                        if result:
                            print(result)
        except FileNotFoundError:
            print(f"File {file_name} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
finally:
    enter = input('Press Enter to exit ')
    os.system('cls||clean')
