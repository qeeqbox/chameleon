__G__ = "(G)bd249ce4"

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning)

from warnings import filterwarnings
filterwarnings(action='ignore', module='.*impacket.*')

from logging import StreamHandler, getLogger, DEBUG
from impacket import smbserver
from impacket.smbconnection import SMBConnection
from tempfile import mkdtemp
from shutil import rmtree
from impacket.ntlm import compute_lmhash, compute_nthash
from multiprocessing import Process
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from logging import DEBUG, basicConfig, getLogger


class QSMBServer():
    def __init__(self, ip=None, port=None, username=None, password=None, mocking=False, logs=None):
        self.ip = ip or '0.0.0.0'
        self.port = port or 445
        self.username = username or "test"
        self.password = password or "test"
        self.mocking = mocking or ''
        self.setup_logger(logs)

    def setup_logger(self, logs):
        self.logs = getLogger("chameleonlogger")
        self.logs.setLevel(DEBUG)
        if logs:
            from custom_logging import CustomHandler
            self.logs.addHandler(CustomHandler(logs))
        else:
            basicConfig()

    def smb_server_main(self):
        _q_s = self

        class Logger(object):
            def write(self, message):
                try:
                    print(message)
                    if "Incoming connection" in message.strip() or "AUTHENTICATE_MESSAGE" in message.strip() or "authenticated successfully" in message.strip():
                        _q_s.logs.info(["servers", {'server': 'http_server', 'action': 'login', 'msg': message.strip()}])
                    elif ":4141414141414141:" in message.strip():
                        parsed = message.strip().split(":")
                        if len(parsed) > 2:
                            _q_s.logs.info(["servers", {'server': 'http_server', 'action': 'login', 'workstation': parsed[0], 'test':parsed[1]}])
                except Exception as e:
                    _q_s.logs.error(["errors", {'server': 'http_server', 'error': 'write', "type": "error -> " + repr(e)}])

        handler = StreamHandler(Logger())
        getLogger("impacket").addHandler(handler)
        getLogger("impacket").setLevel(DEBUG)
        dirpath = mkdtemp()
        server = smbserver.SimpleSMBServer(listenAddress=self.ip, listenPort=self.port)
        # server.removeShare("IPC$")
        server.addShare('C$', dirpath, '', readOnly='yes')
        server.setSMB2Support(True)
        server.addCredential(self.username, 0, compute_lmhash(self.password), compute_nthash(self.password))
        server.setSMBChallenge('')
        server.start()
        rmtree(dirpath)

    def run_server(self, process=False):
        self.close_port()
        if process:
            self.smb_server = Process(name='QSMBServer_', target=self.smb_server_main)
            self.smb_server.start()
        else:
            self.smb_server_main()

    def kill_server(self, process=False):
        self.close_port()
        if process:
            self.smb_server.terminate()
            self.smb_server.join()

    def test_server(self, ip=None, port=None, username=None, password=None):
        try:
            sleep(2)
            _ip = ip or self.ip
            _port = port or self.port
            _username = username or self.username
            _password = password or self.password
            smb_client = SMBConnection(_ip, _ip, sess_port=_port)
            smb_client.login(_username, _password)
        except Exception:
            pass

    def close_port(self):
        for process in process_iter():
            try:
                for conn in process.connections(kind='inet'):
                    if self.port == conn.laddr.port:
                        process.send_signal(SIGTERM)
                        process.kill()
            except BaseException:
                pass

#parsed = server_arguments()

# if parsed.docker or parsed.aws or parsed.custom:
#	qrdpserver = QRDPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
#	qrdpserver.run_server()
#
# if parsed.test:
#	qrdpserver = QRDPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
#	qrdpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
