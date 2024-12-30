# Python Dark Programming Language

Приветствую вас в **Python Dark Programming Language** — моём собственном языке программирования, созданном на всем известном Python. Этот проект создан в целях исследования новых возможностей и изучения Python.

## Документация

[https://vsp210.github.io/Docs-for-Dark-lang](https://vsp210.github.io/Docs-for-Dark-lang)

## Описание

Dark — это язык программирования, созданный мной в 14 лет.

## Контакты
ВКонтакте: https://vk.com/vsp210
Телеграм: https://t.me/vsp210
Моё портфолио: https://vsp210.github.io/portfolio/


# Обновление:

#### Наконец версия для Linux

#### В последней версии добавлены следующие функции:
- Модифицирование - это возможность создавать свои модификации на языке программирования Python и подключать к языку программирования Dark: Пример:
```
   /mods/                 - Создаём папку для модификаций
      /test/              - Создаём папку с именем модификации
         /initialize.py   - Файл для инициализации модификаций
         /main.py         - Файл для основной логики модификации
   /DarkInstaller.exe - используйте для установки модификаций инструкция на сайте https://psv449.pythonanywhere.com/

```
- [**main.py**]():
```python
def hi_function(*args):
    return str(args) + ' - Hi'

def bye_function(*args):
    return str(args) + ' - Bye'
```
- [**initialize.py**]()
```python
from dark_lang_code.classes import add_mod

add_mod('hi', hi_function)
add_mod('bye', bye_function)
```

##### Теперь можно использовать модификацию в Dark
```dark
mods init

import hi
import bye

hi Привет

set str text Пока

bye [{ text }]
```

###### Этот модификатор позволяет выводить любой текст с текстом Hi или Bye

##### Теперь можно совершать импорты к другим фаилам .dark
Пример:

file1.dark:
```dark
<-#-> Импорт переменной:
from путь/до/file2.dark import_var test
<-#-> Иморт блока:
from путь/до/file2.dark import_block test_block

<-#-> Вывод переменной и запуск блока:
output [{test}]
run test_block
```

file2.dark:
```dark
<-#-> Переменная:
set str test := Hello World
<-#-> Блок:
block test_block :
> output Hi, I Dark!
endblock
```

##### Вывод:
```bash
Hello World
Hi, I Dark!
```
