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
            if any(line.startswith(f'set {var_type} {variable_name} ') for var_type in ["int", "str", "list", "dict", "bool", "float"]):
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
        return output_string.strip()

    def set_variable(self, var_type: str, name_value: str, output: bool = False) -> str:
        try:
            match = re.match(r'^\s*(.*?)\s*:=\s*(.*?)\s*$', name_value)
            name, value = match.groups()
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
            elif var_type == "float":
                variable = FloatVariable(name, float(value))
            else:
                raise VariableError(f"Unknown variable type '{var_type}'.")

            self.variable_store.add_variable(variable)
            return f"Variable '{name}' set." if output else None
        except Exception as e:
            return f"Error setting variable: {e}"

    def delete_variable(self, name, output=False):
        if self.variable_store.delete_variable(name):
            if output:
                return f"Variable '{name}' deleted."
        else:
            raise VariableError(f"Variable '{name}' not found.")

    def input_variable(self, var_type, name, prompt):
        prompt = prompt.replace('\\n', '\n').replace('\\s', ' ')
        value = input(prompt)
        name_value = name + ':=' + value
        return self.set_variable(var_type, name_value)

    def processing_if(self, condition, command_if):
        condition = condition.strip()
        command_if_ls = command_if.split('/|\\')

        if condition.startswith('[{') and condition.endswith('}]'):
            var_name = condition[2:-2].strip()
            var = self.variable_store.get_variable(var_name)
            if not var:
                raise VariableError("Unknown variable")
            condition_value = var.value
        else:
            condition_value = condition

        if '==' in condition:
            left, right = map(str.strip, condition.split('=='))
            if left == right:
                for command in command_if_ls:
                    self.execute(command)
        elif '>>' in condition:
            left, right = map(str.strip, condition.split('>>'))
            if float(left) > float(right):
                for command in command_if_ls:
                    self.execute(command)
        elif '<<' in condition:
            left, right = map(str.strip, condition.split('<<'))
            if float(left) < float(right):
                for command in command_if_ls:
                    self.execute(command)
        elif condition_value:
            if isinstance(condition_value, bool):
                for command in command_if_ls:
                    self.execute(command)
        else:
            raise SyntaxError("Invalid condition syntax")

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

    def update(self, *args):
        text = ' '.join(args)
        variable, upd_value = text.split(':=')
        variable = variable.strip()
        var = self.variable_store.get_variable(variable)
        if var:
            var.value = upd_value.strip()
        else:
            raise VariableError("Unknown variable - {name}".format(name=var))


    def execute(self, command):
        try:
            parts = command.split()
            if parts[0] == "mods":
                if parts[1] == "init":
                    initialize_moduls()
            elif parts[0] == "set":
                if parts[1] == "output":
                    var_type = parts[2]
                    name_value = ' '.join(parts[3:])
                    return self.set_variable(var_type, name_value, output=True)
                elif parts[1] == "block":
                    arrow_index = parts.index('=>')
                    name_block = parts[2].strip()
                    command_block = ' '.join(parts[arrow_index + 1:])
                    return self.set_block(name_block, command_block)
                elif len(parts) >= 4:
                    var_type = parts[1]
                    name_value = ' '.join(parts[2:])
                    return self.set_variable(var_type, name_value)
            elif parts[0] == "input":
                if parts[1] == "->":
                    var_type = parts[2]
                    name = parts[3]
                    prompt = ' '.join(parts[4:])
                    return self.input_variable(var_type, name, prompt)
                else:
                    raise CommandError("Invalid input command. Did you forget to add ->?")
            elif parts[0] == 'upd':
                return self.update(*parts[1:])
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
                arrow_index = parts.index('>=')
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
                                block = self.block_store.get_block(var_name)
                                if block:
                                    block = block.split('\|/')
                                    for command in block:
                                        args.append(command)
                                else:
                                    args.append(arg)
                        else:
                            args.append(arg)

                    return mod(*args)
                else:
                    raise VariableError(f"Unknown line - '{' '.join(parts)}'.")
        except VariableError as e:
            return (f"Error: {e}")
