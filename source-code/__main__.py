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


        # file_name = 'test.dark'

        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        result = command_processor.execute(line)
                        if result:
                            print(result)
        except FileNotFoundError:
            print(f"File {file_name} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
finally:
    input('Press Enter to exit')
