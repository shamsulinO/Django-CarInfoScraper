Russian Version

Парсинг объявлений с сайта avito.ru и получение информации об авто из открытых источников.

Парсер собирает все объявления по указанным условиям и выдает вам в виде списка на сайте. При нажатии на объявление
можно получить более подробную информацию. При появлении на сайте нового объявления вам придет письмо на почту 
(можно выключить в настройках)

Подготовка:
1) В файле aparser/aparser/acars/utils/acars/parser.py добавить почту отправителя и его пароль.
2) В файле aparser/apaser/aparser/settings.py добавить почту отправителя и его пароль.

Запуск:
1) Сайт - Из папки aparser/aparser выполняем команду в терминале: python manage.py runserver
2) Парсер - Из папки aparser/aparser/acars/utils/acars выполняем команду в терминале: python parser.py

_________________________________________________________________________________

English Version

Parsing advertisements from the website avito.ru and obtaining information about cars from open sources

The parser collects all advertisements based on the specified criteria and presents them to you in the form of a list 
on the website. By clicking on an advertisement, you can get more detailed information. When a new advertisement appears
on the website, you will receive an email notification (which can be disabled in the settings).

Preparation:
1) In the file aparser/aparser/acars/utils/acars/parser.py, add the sender's email address and its password.
2) In the file aparser/apaser/aparser/settings.py, add the sender's email address and its password.

Execution:
1) Website - From the aparser/aparser folder, execute the command in the terminal: python manage.py runserver
2) Parser - From the aparser/aparser/acars/utils/acars folder, execute the command in the terminal: python parser.py
