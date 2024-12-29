import os
import sys
import time

try:
    from dark_lang_code.dark import CommandProcessor
    from dark_lang_code.classes import VariableStore, BlockStore

    if __name__ == "__main__":
        store = VariableStore()
        block_store = BlockStore()
        command_processor = CommandProcessor(store, block_store)

        args = sys.argv

        # if len(args) < 2:
        #     print("No file scripts")
        #     sys.exit(1)

        # file_name = args[1]


        file_name = 'test.dark'
        debug = False
        line_number = 0

        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    line_number += 1
                    line = line.strip()
                    if line == '<-#-> dark debug start':
                        print(f"\033[38;2;0;0;0m{line_number}. start - debug mode\033[0m")
                        debug = True
                        continue
                    if line == '<-#-> dark debug stop':
                        print(f"\033[38;2;0;0;0m{line_number}. stop - debug mode\033[0m")
                        debug = False
                        continue
                    if line.strip().split(' ')[0] == '<-#->':
                        if line.strip().split(' ')[1] == 'dark':
                            pass
                        else:
                            continue
                    if line:
                        if debug:
                            print(f"\033[38;2;255;255;0m{line_number}. {line}\033[0m"+':')
                            time.sleep(0.5)
                        result = command_processor.execute(line, line_number)
                        if result is None and debug:
                            if line.strip().split(' ')[0] == 'set':
                                print('Creating a variable/block.')
                            elif line.strip().split(' ')[0] == 'delete':
                                print('Deleting a variable.')
                            elif line.strip().split(' ')[0] == 'input':
                                pass
                        if result:
                            print(result)
        except FileNotFoundError:
            print(f'\033[38;2;255;0;0mFile {file_name} not found.\033[0m')
        except Exception as e:
            print(f'\033[38;2;255;0;0mError: {e}\033[0m')
finally:
    enter = input('\033[38;2;255;255;0mPress Enter to exit \033[0m')
    if enter == "not purify":
        pass
    else:
        os.system('cls||clear')
