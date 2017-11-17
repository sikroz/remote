import subprocess
import config


class Server:
    def __init__(self):
        self.host = config.BUILD_HOST
        self.port = config.BUILD_PORT

    def upload(self, path, exclude):
        self.ssh('mkdir -p {path}'.format(path=path))
        cmd = (
            'rsync -trvlH'
            ' -e "ssh -p {port}"'
            ' {exclude}'
            ' --delete'
            ' {src}/ root@{host}:{dst}').format(
                host=self.host,
                port=self.port,
                src=path,
                dst=path,
                exclude=reduce(lambda x, y: x + ' --exclude {}'.format(y), exclude, '')
                )
        print cmd
        subprocess.check_call(cmd, shell=True)

    def download(self, path, exclude):
        cmd = (
            'rsync -trvlH'
            ' -e "ssh -p {port}"'
            ' {exclude}'
            ' --delete'
            ' root@{host}:{src}/ {dst}').format(
                host=self.host,
                port=self.port,
                src=path,
                dst=path,
                exclude=reduce(lambda x, y: x + ' --exclude {}'.format(y), exclude, '')
                )
        print cmd
        subprocess.check_call(cmd, shell=True)

    def ssh(self, command):
        cmd = 'ssh -A -p {port} root@{host} "{cmd}"'.format(port=self.port, host=self.host, cmd=command)
        subprocess.check_call(cmd, shell=True)

    def ssh_cd(self, wd, command):
        self.ssh('cd {wd}; {cmd}'.format(wd=wd, cmd=command))


