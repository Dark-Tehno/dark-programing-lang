import re
from .mod import initialize_moduls
from .classes import *
import os

class CommandProcessor:
    def __init__(self, variable_store, block_store):
        self.variable_store = variable_store
        self.block_store = block_store
        self.mods = {}

    def from_import_block(self, file, block_name):
        if not os.path.isfile(file):
            raise CommandError(f"File '{file}' not found.")

        with open(file, 'r') as file:
            lines = file.readlines()
        for line in lines:
            if line.startswith(f'set block {block_name} => '):
                self.block_store.add_block(block_name, line.split('=>')[1].strip())
                return


    def from_import_variable(self, file, variable_name):
        if not os.path.isfile(file):
            raise CommandError(f"File '{file}' not found.")

        with open(file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if any(line.startswith(f'set {var_type} {variable_name} ') for var_type in ["int", "str", "list", "dict", "bool"]):
                parts = line.split(' ')
                var_type = parts[1]
                name = parts[2]
                value = ' '.join(parts[3:])
                self.set_variable(var_type, name, value)
                return


    def output(self, *args):
        output_string = ' '.join(args)
        output_string = output_string.replace('\\n', '\n').replace('\\s', ' ')
        output_string = re.sub(r'\[\{(.*?)\}\]', lambda match: str(self.variable_store.get_variable(match.group(1).strip()).value), output_string)
        output_string = re.sub(r'\[\{\s*', '[{', output_string)
        output_string = re.sub(r'\s*\}\]', '}]', output_string)
        print(output_string.strip())
        return

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
            elif var_type == "dict":
                pairs = value.split('|')
                dict_value = {}
                for pair in pairs:
                    key, val = pair.split('=>')
                    dict_value[key.strip()] = val.strip()
                variable = DictVariable(name, dict_value)
            elif var_type == "bool":
                if value == "true" or value == "True" or value == 1 or value == '1':
                    variable = BoolVariable(name, True)
                else:
                    variable = BoolVariable(name, False)
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
                    elif var_type == "dict":
                        pairs = value.split('|')
                        dict_value = {}
                        for pair in pairs:
                            key, val = pair.split('=>')
                            dict_value[key.strip()] = val.strip()
                        new_variable = DictVariable(name, dict_value)
                    elif var_type == "bool":
                        new_variable = BoolVariable(name, bool(value))
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
            condition_ls = condition.split(' ')
            if len(condition_ls) == 1:
                condition = ' '.join(condition_ls)
                var_name = condition.strip('[{}]')
                var_value = condition[1].strip()
                var = self.variable_store.get_variable(var_name)

                if var:
                    if isinstance(var, BoolVariable):
                        if var.value == True:
                            command_if_ls = command_if.split('\|/')
                            if list(command_if_ls):
                                for command in command_if_ls:
                                    self.execute(command)
                            else:
                                self.execute(command_if)
                        else:
                            return
                    else:
                        raise SyntaxError
                else:
                    raise VariableError("Unknown variable")

    def set_block(self, name_block, command_block):
        if name_block is not None and command_block is not None:
            self.block_store.add_block(name_block, command_block)
        else:
            raise CommandError("Invalid block command.")

    def import_mod(self, name):
        if name is not None:
            mod = get_mod(name)
            if mod:
                self.mods[name] = mod
            else:
                raise CommandError("Unknown module - {name}".format(name=name))
        else:
            raise CommandError("Invalid module name")



    def execute(self, command):
        try:
            parts = command.split()
            if parts[0] == "mods":
                if parts[1] == "init":
                    initialize_moduls()
            elif parts[0] == "set":
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
                elif parts[1] == "block":
                    arrow_index = parts.index('=>')
                    name_block = parts[2].strip().strip('[{}]')
                    command_block = ' '.join(parts[arrow_index + 1:])
                    return self.set_block(name_block, command_block)
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
                    var_type = parts[1] if parts[1] in ["int", "str", "list", "dict", "bool"] else None
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
            elif parts[0] == "run-block":
                name_block = parts[1]
                block = self.block_store.get_block(name_block)
                if block:
                    block = block.split('\|/')
                    for command in block:
                        result = self.execute(command)
                        if result:
                            return result
                else:
                    raise CommandError(f"Block '{name_block}' not found.")
            elif parts[0] == "import":
                name = parts[1]
                return self.import_mod(name)

            elif parts[0] == "from":
                file = parts[1]
                if parts[2] == "import_block":
                    block = parts[3]
                    self.from_import_block(file, block)

                elif parts[2] == "import_var":
                    variable = parts[3]
                    self.from_import_variable(file, variable)
                else:
                    raise CommandError(f"Invalid import command - '{' '.join(parts)}'.")
            else:
                mod = self.mods.get(parts[0], None)
                if mod is not None:
                    args = []
                    for arg in parts[1:]:
                        if arg.startswith('[{') and arg.endswith('}]'):
                            var_name = arg[2:-2]
                            variable = self.variable_store.get_variable(var_name)
                            if variable:
                                args.append(variable.value)
                            else:
                                args.append(arg)
                        else:
                            args.append(arg)

                    return mod(*args)
                else:
                    raise VariableError(f"Unknown line - '{' '.join(parts)}'.")
        except VariableError as e:
            return (f"Error: {e}")
