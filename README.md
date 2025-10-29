# Диспетчер сообщений (messages dispatcher) udp2udp

Предназначен для передачи информации между автоматизированными системами (сегментами автоматизированных систем) в которых обрабатывается информация с различной степенью конфиденциальности или различными правилами присвоения мандатных меток.

За основу взяты проекты
"""
https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df
https://gist.github.com/vxgmichel/e47bff34b68adb3cf6bd4845c4bed448
https://gist.github.com/giacobenin/e1534638609a0dfb17b91c81da33c023 # Пример работает, но только в одну сторону, обратные сообщения вызывают ошибку, нужно разбираться
https://github.com/jsbronder/asyncio-dgram/tree/master
https://anyio.readthedocs.io/en/latest/index.html
"""

Зависимости:
python3-jsonschema
python3-lxml

udp2udp.py
Ожидает получения сообщения от клиента, выполняет его валидацию в соответствии с заданной в настройках схемой, в случае успешной валидации отправляет сообщение серверу

msg2udp.py
Читает сообщение из стандартного ввода или файла, имя которого задано первым аргументом, и отправляет диспетчеру доступа

udp2msg.py
Ожидает получения сообщения от диспетчера доступа и отправляет диспетчеру ответ


# Компиляция в Astra Linux SE 1.7
Установка pip из репозитория base
$sudo apt install python3-pip
Под учетной записью пользователя (не рута) установить nuitka (нужен доступ в интернет)
$python -m pip install nuitka
$python3 -m nuitka --version

2.8.4
Commercial: None
Python: 3.7.3 (default, Jul 21 2025, 15:56:22) 
Flavor: Debian Python
Executable: /usr/bin/python3
OS: Linux
Arch: x86_64
Distribution: Astra (based on Debian) None
Version C compiler: /usr/bin/gcc (gcc 8).

$sudo apt install zlib1g-dev

## Компиляция программы
(см.: https://pypi.org/project/Nuitka/)
$python -m nuitka udp2udp.py
В итоге получаем исполняемый файл udp2udp.bin и каталог udp2udp.build с объектными файлами, сгенерированными при компиляции
$ldd udp2udp.bin 
	linux-vdso.so.1 (0x00007ffc2aac8000)
	libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x000078fb7ea7a000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x000078fb7e8f7000)
	libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x000078fb7e8d9000)
	libutil.so.1 => /lib/x86_64-linux-gnu/libutil.so.1 (0x000078fb7e8d4000)
	libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x000078fb7e8b3000)
	libexpat.so.1 => /lib/x86_64-linux-gnu/libexpat.so.1 (0x000078fb7e876000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x000078fb7e6b3000)
	/lib64/ld-linux-x86-64.so.2 (0x000078fb7eaa8000)
NB! Успешно запускается, но требует, чтобы validate.py был в одном каталоге с исполняемым файлом

При компиляции программы с опцией --follow-imports на отсутствие в одном каталоге validate.py не жалуется, но получаем ошибку
2025-10-28 01:10:08 DEBUG Try loading request.json schema...
Traceback (most recent call last):
  File "/tmp/dispatcher/validator.py", line 53, in validator
    xmlschema = etree.XMLSchema(etree.parse(schema))
AttributeError: module 'lxml.etree' has no attribute 'XMLSchema'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/tmp/dispatcher/udp2udp.py", line 31, in <module>
    local_validate = validator.validator(config.get("local", "schema", fallback=""))
  File "/tmp/dispatcher/validator.py", line 58, in validator
    except etree.XMLSyntaxError as err:
AttributeError: module 'lxml.etree' has no attribute 'XMLSyntaxError'

NB! Нужно почитать мануал nuitka, чтобы понять как правильно скомпилировать программу



NB! В JSON валидаторе при работе с регулярками необходимо четко указывать якоря начала и окончания строки, иначе пропускает несоответствие формата

pdp-exec [опции] -- [команда]
Утилита для запуска процессов в заданном окружении

Синтаксис команды:
pdp-exec [параметр[параметр...]] [--] <команда_запуска_процесса> [параметры_запуска_процесса]
В случае если с командой заданы параметры ее запуска, то указание символов «--» перед командой обязательно.

Опции:
        -v --version    Версия утилиты
        -h --help       Справка по использованию
        -c <привилегии>, --capability=<привилегии>
                Установить эффективные, наследуемые и разрешенные привилегии процесса в указанное значение
        -e <привилегии>, --effective=<привилегии>
                Установить эффективные привилегии процесса в указанное значение. По умолчанию 0
        -i <привилегии>, --inheritable=<привилегии>
                Установить наследуемые привилегии процесса в указанное значение. По умолчанию 0
        -p <привилегии>, --permitted=<привилегии>
                Установить разрешенные привилегии процесса в указанное значение. По умолчанию 0
        -u <имя пользователя>, --user=<имя пользователя>
                Запуск от имени указанного пользователя (необязательный параметр)
        -l <метка>, --label=<метка>
                Мандатная метка процесса (необязательный параметр)

execaps [опции] -- [команда]
Утилита для запуска процессов с указанными привилегиями.
Опции:
        -v --version    Версия утилиты.
        -h --help       Справка по использованию.
        -c <привилегии>, --capability=<привилегии>      Установить эффективные, наследуемые и разрешенные привилегии процесса в указанное значение.
        -e <привилегии>, --effective=<привилегии>       Установить эффективные привилегии процесса в указанное значение. По умолчанию 0.
        -i <привилегии>, --inheritable=<привилегии>     Установить наследуемые привилегии процесса в указанное значение. По умолчанию 0.
        -p <привилегии>, --permitted=<привилегии>       Установить разрешенные привилегии процесса в указанное значение. По умолчанию 0.
        -f --force      Запустить процесс, даже если не удалось установить полномочия.


pscaps [--version] [-h, --help] [действующие полномочия [разрешенные полномочия [наследуемые полномочия]]]
Команда pscaps может быть использована для просмотра и изменения (в численном виде) PARSEC-полномочий процесса.
pscaps [effective_caps [permitted_caps [inheritable_caps]]]
Если в качестве аргумента указан только идентификатор процесса, то команда показывает набор полномочий заданного процесса, в противном случае пытается установить заданные в командной строке в виде шестнадцатеричных чисел полномочия.


Запуск приложения с мандатной меткой 2:0:0x3:0
sudo pdp-exec -u admsec -l 1:0:0x0 bash

Для запуска службы systemd с определенной меткой безопасности необходимо в конфигурационном файле (юните) соответствующей службы (<имя_юнита>.service) в разделе
[Service] добавить следующий параметр (метку):
PDPLabel=<Уровень>:<Категория_целостности>:<Категории>


Использование диспетчера в Astra Linux с привилегией PARSEC_CAP_PRIV_SOCK для проксирования датаграмм между узлами с разными уровнями конфиденциальности
sudo execaps -c 0x100 -- /home/m6v/Workspace/dispatcher/udp2udp.py

Отправка сообщения в серверный UDP-сокет
echo '{"id": 1, "name": "Sergey Maksimov", "age": 52}' > /dev/udp/127.0.0.1/14550

Захват пакетов
sudo tcpdump -i any udp port 14550 or port 12200


# asyncio.get_event_loop(): DeprecationWarning: There is no current event loop

Your code will run on Python3.10 but as of 3.11 it will be an error to call asyncio.get_event_loop when there is no running loop in the current thread. Since you need loop as an argument to amain, apparently, you must explicitly create and set it.
It is better to launch your main task with asyncio.run than loop.run_forever, unless you have a specific reason for doing it that way. [But see below]
Try this:
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(amain(loop=loop))
    except KeyboardInterrupt:
        pass
Added April 15, 2023:
There is a difference between calling asyncio.run(), which I have done here, and calling loop.run_forever() (as in the original question) or loop.run_until_complete(). When I wrote this answer I did not realize that asyncio.run() always creates a new event loop. Therefore in my code above, the variable loop that is passed to amain will not become the "running loop." So my code avoids the DeprecationWarning/RuntimeException, but it doesn't pass a useful loop into amain.
To correct that, replace the line
asyncio.run(amain(loop=loop))
with
loop.run_until_complete(amain(loop=loop))
It would be best to modify amain to obtain the running event loop inside the function instead of passing it in. Then you could launch the program with asyncio.run. But if amain cannot be changed that won't be possible.
Note that run_until_complete, unlike asyncio.run, does not clean up async generators. This is documented in the standard docs.
