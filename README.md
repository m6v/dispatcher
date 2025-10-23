# Диспетчер сообщений (messages dispatcher) udp2udp

За основу взяты проекты
"""
https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df
https://gist.github.com/giacobenin/e1534638609a0dfb17b91c81da33c023
"""

Зависимости (если будут использоваться json сообщения):
python3-jsonschema
python3-jinja2


udp2udp.py
Ожидает получения сообщения от клиента, выполняет его валидацию в соответствии с заданной в настройках схемой, в случае успешной валидации отправляет сообщение серверу

msg2udp.py
Читает сообщение из стандартного ввода или файла, имя которого задано первым аргументом, и отправляет диспетчеру доступа

udp2msg.py
Ожидает получения сообщения от диспетчера доступа и отправляет диспетчеру ответ

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

pdp-exec [опции] -- [команда]
Утилита для запуска процессов в заданном окружении
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


Запуск приложения с мандатной меткой 2:0:0x3:0
sudo pdp-exec -u admsec -l 1:0:0x0 bash

Использование диспетчера в Astra Linux с привилегией PARSEC_CAP_PRIV_SOCK для проксирования датаграмм между узлами с разными уровнями конфиденциальности
sudo execaps -c 0x100 -- /home/m6v/Workspace/dispatcher/udp2udp.py

Отправка сообщения в серверный UDP-сокет
echo '{"id": 1, "name": "Sergey Maksimov", "age": 52}' > /dev/udp/127.0.0.1/14550

Захват пакетов
tcpdump -i lo udp port 14550 or port 12200


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
