class Variable:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name


class IntVariable(Variable):
    def __init__(self, name, value):
        super().__init__(name, int(value))

class StrVariable(Variable):
    def __init__(self, name, value):
        super().__init__(name, str(value))

class ListVariable(Variable):
    def __init__(self, name, value):
        super().__init__(name, list(value))

class VariableStore:
    def __init__(self):
        self.variables = {}

    def add_variable(self, variable):
        self.variables[variable.name] = variable

    def get_variable(self, name):
        return self.variables.get(name)

    def delete_variable(self, name):
        if name in self.variables:
            del self.variables[name]
            return True
        return False

class VariableError(Exception):
    pass

class CommandProcessor:
    def __init__(self, variable_store):
        self.variable_store = variable_store

    def output(self, *args):
        output_string = ' '.join(args)
        output_string = output_string.replace('\\n', '\n')
        output_string = output_string.replace('\\s', ' ')

        for var_name in self.variable_store.variables:
            output_string = output_string.replace('[{'+var_name+'}]', str(self.variable_store.get_variable(var_name).value))
            if '[{'f'{var_name}''.type}]' in output_string:
                output_string = output_string.replace('[{'f'{var_name}''.type}]', str(type(self.variable_store.get_variable(var_name).value)))
            else:
                output_string = output_string.replace('[{'f'{var_name}''}]', str(self.variable_store.get_variable(var_name).value))

        while '\\erase' in output_string:
            erase_index = output_string.index('\\erase')
            if erase_index > 0 and erase_index < len(output_string) - 7:
                output_string = output_string[:erase_index - 1] + output_string[erase_index + 7:]
            else:
                output_string = output_string[:erase_index] + output_string[erase_index + 7:]

        print(output_string.strip())

    def set_variable(self, var_type: str, name: str, value: str, output: bool = False) -> str:
        try:
            value = value.replace('\\n', '\n').replace('\\s', ' ')

            if var_type == "int":
                variable = IntVariable(name, value)
            elif var_type == "str":
                variable = StrVariable(name, value)
            elif var_type == "list":
                value = value.split('|')
                variable = ListVariable(name, value)
            else:
                raise VariableError(f"Unknown variable type '{var_type}'.")

            self.variable_store.add_variable(variable)
            return f"Variable '{name}' set." if output else ""
        except Exception as e:
            return f"Error setting variable: {e}"

    def update_variable(self, var_type, name, value, output=False):
        try:
            variable = self.variable_store.get_variable(name)
            if variable:
                if var_type:
                    if var_type == "int":
                        new_variable = IntVariable(name, int(value))
                    elif var_type == "str":
                        new_variable = StrVariable(name, str(value))
                    elif var_type == "list":
                        value = value.split('|')
                        new_variable = ListVariable(name, list(value))
                    else:
                        raise VariableError(f"Unknown variable type '{var_type}'.")

                    self.variable_store.add_variable(new_variable)
                    if output:
                        return f"Variable '{name}' updated to new type '{var_type}' with value '{value}'."
                else:
                    variable.value = value
                    if output:
                        return f"Variable '{name}' updated."
            else:
                raise VariableError(f"Variable '{name}' not found.")
        except Exception as e:
            return (f"Variable update error: {e}")


    def delete_variable(self, name, output=False):
        if self.variable_store.delete_variable(name):
            if output:
                return f"Variable '{name}' deleted."
        else:
            raise VariableError(f"Variable '{name}' not found.")

    def input_variable(self, var_type, name, prompt):
        prompt = prompt.replace('\\n', '\n').replace('\\s', ' ')
        value = input(prompt)
        return self.set_variable(var_type, name, value)

    def processing_if(self, condition, command_if):
        if condition:
            condition_ls = condition.split('==')
            if len(condition_ls) == 2:
                var_name = condition_ls[0].strip().strip('[{}]')
                var_value = condition_ls[1].strip()
                var = self.variable_store.get_variable(var_name)
                if var:
                    if str(var.value) == var_value:
                        command_if_ls = command_if.split('\|/')
                        if list(command_if_ls):
                            for command in command_if_ls:
                                self.execute(command)
                        else:
                            self.execute(command_if)
                else:
                    raise VariableError("Unknown variable")
            condition_ls = condition.split('>')
            if len(condition_ls) == 2:
                var_name = condition_ls[0].strip().strip('[{}]')
                var_value = condition_ls[1].strip()
                var = self.variable_store.get_variable(var_name)
                if var:
                    if int(var.value) > int(var_value):
                        command_if_ls = command_if.split('\|/')
                        if list(command_if_ls):
                            for command in command_if_ls:
                                self.execute(command)
                        else:
                            self.execute(command_if)
                else:
                    raise VariableError("Unknown variable")
            condition_ls = condition.split('<')
            if len(condition_ls) == 2:
                var_name = condition_ls[0].strip().strip('[{}]')
                var_value = condition_ls[1].strip()
                var = self.variable_store.get_variable(var_name)
                if var:
                    if int(var.value) < int(var_value):
                        command_if_ls = command_if.split('\|/')
                        if list(command_if_ls):
                            for command in command_if_ls:
                                self.execute(command)
                        else:
                            self.execute(command_if)
                else:
                    raise VariableError("Unknown variable")

    def execute(self, command):
        try:
            parts = command.split()
            if parts[0] == "set":
                if parts[1] == "output":
                    var_type = parts[2]
                    name = parts[3]
                    value = parts[4]
                    return self.set_variable(var_type, name, value, output=True)
                elif parts[1] == "input":
                    var_type = parts[2]
                    name = parts[3]
                    prompt = ' '.join(parts[4:])
                    return self.input_variable(var_type, name, prompt)
                elif len(parts) >= 4:
                    var_type = parts[1]
                    name = parts[2]
                    value = ' '.join(parts[3:])
                    return self.set_variable(var_type, name, value)
            elif parts[0] == "update":
                if parts[1] == "output":
                    var_type = parts[2]
                    name = parts[3]
                    value = parts[4]
                    return self.update_variable(var_type, name, value, output=True)
                elif len(parts) >= 3:
                    var_type = parts[1] if parts[1] in ["int", "str", "list"] else None
                    name = parts[1] if var_type is None else parts[2]
                    value = ' '.join(parts[2:]) if var_type is None else ' '.join(parts[3:])
                    return self.update_variable(var_type, name, value)
            elif parts[0] == "delete":
                if parts[1] == "output":
                    name = parts[2]
                    return self.delete_variable(name, output=True)
                elif len(parts) == 2:
                    name = parts[1]
                    return self.delete_variable(name)
            elif parts[0] == "output":
                return self.output(*parts[1:])
            elif parts[0] == "<-#->":
                return
            elif parts[0] == "if":
                arrow_index = parts.index('=>')
                condition = ' '.join(parts[1:arrow_index])
                command_if = ' '.join(parts[arrow_index + 1:])
                return self.processing_if(condition, command_if)
            else:
                raise VariableError(f"Unknown line - '{' '.join(parts)}'.")
        except VariableError as e:
            return (f"Error: {e}")

store = VariableStore()
command_processor = CommandProcessor(store)


import sys

if __name__ == "__main__":
    store = VariableStore()
    command_processor = CommandProcessor(store)

    # args = sys.argv

    # if len(args) < 2:
    #     print("No file scripts")
    #     sys.exit(1)

    # file_name = args[1]


    file_name = 'test.dark'

    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    result = command_processor.execute(line)
                    if result:
                        print(result)
            input('Press Enter to exit')
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
