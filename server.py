import subprocess
import config


class Server:
    def __init__(self):
        self.user = config.BUILD_USER
        self.host = config.BUILD_HOST
        self.port = config.BUILD_PORT

    def upload(self, local_path, remote_path, exclude):
        self.ssh('mkdir -p {path}'.format(path=remote_path))
        cmd = (
            'rsync -trvlH'
            ' -e "ssh -p {port}"'
            ' {exclude}'
            ' --delete'
            ' {src}/ {user}@{host}:{dst}').format(
                user=self.user,
                host=self.host,
                port=self.port,
                src=local_path,
                dst=remote_path,
                exclude=reduce(lambda x, y: x + ' --exclude {}'.format(y), exclude, '')
                )
        print cmd
        subprocess.check_call(cmd, shell=True)

    def download(self, remote_path, local_path, exclude):
        cmd = (
            'rsync -trvlH'
            ' -e "ssh -p {port}"'
            ' {exclude}'
            ' --delete'
            ' {user}@{host}:{src}/ {dst}').format(
                user=self.user,
                host=self.host,
                port=self.port,
                src=remote_path,
                dst=local_path,
                exclude=reduce(lambda x, y: x + ' --exclude {}'.format(y), exclude, '')
                )
        print cmd
        subprocess.check_call(cmd, shell=True)

    def download_tar(self, remote_path, local_path):
        cmd = (
            'ssh -p {port} {user}@{host} "cmd tar -czf - -C {src} ." | tar -xzf - -C {dst}').format(
                user=self.user,
                host=self.host,
                port=self.port,
                src=remote_path,
                dst=local_path,
                )
        print cmd
        subprocess.check_call(cmd, shell=True)


    def ssh(self, command):
        cmd = 'ssh -A -p {port} {user}@{host} "{cmd}"'.format(user=self.user, port=self.port, host=self.host, cmd=command)
        subprocess.check_call(cmd, shell=True)

    def ssh_cd(self, wd, command):
        self.ssh('cd {wd}; {cmd}'.format(wd=wd, cmd=command))


