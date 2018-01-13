#!/usr/bin/python
import sys
import os
import subprocess
from server import Server
import config

def escape(args):
    result = []
    for a in args:
        if ' ' in a:
            result.append("'{}'".format(a))
        else:
            result.append(a)
    return result

def main():
    server = Server()
    local_cwd = os.getcwd()
    remote_cwd = local_cwd.replace(config.SRC, config.REMOTE_SRC)
    log = open('/tmp/cmd.log', 'a')
    log.write('argv: ' + str(sys.argv) + '\n')
    log.write('cwd: ' + local_cwd + '\n')
    log.close()

    argv = sys.argv
    argv0 = argv[0]
    argv0 = argv0.split('/')[-1]
    argv[0] = argv0

    if local_cwd.startswith(config.SRC):
        upload_exclude = ['.git']
        if os.path.exists(os.path.join(local_cwd, '..', 'conanfile.txt')) or os.path.exists(os.path.join(local_cwd, '..', 'conanfile.py')):
            local_parent = os.path.normpath(os.path.join(local_cwd, '..'))
            upload_exclude.append(local_cwd.replace(local_parent, ''))
        else:
            local_parent = local_cwd

        remote_parent = local_parent.replace(config.SRC, config.REMOTE_SRC)
            
        server.upload(local_parent, remote_parent, upload_exclude)

        argv.insert(0, 'IN_DOCKER_HOME=' + config.HOME)
        server.mkdir(remote_cwd)
        if argv0 == 'conan':
            #argv.insert(0, 'CONANHOME=' + config.REMOTE_CONANHOME)
            server.ssh_cd(remote_cwd, ' '.join(escape(argv)))
            if 'info' in argv:
                return
            server.download(os.path.join(config.REMOTE_CONANHOME, '.conan'), os.path.join(config.CONANHOME, '.conan'), [])
        elif argv0 == 'cmake':
            server.ssh_cd(remote_cwd, ' '.join(escape(argv)))
        elif argv0 == 'make':
            server.ssh_cd(remote_cwd, ' '.join(escape(argv)))

        if local_parent != local_cwd:
            server.download(remote_cwd, local_cwd, [])
    else:
        if argv[1] == '-version':
            print 'cmake3 version 3.6.3'
            #server.ssh(' '.join(escape(argv)), do_debug=False)
        elif len(argv) == 4 and argv[3].startswith('/private/'):
            server.upload(argv[3], argv[3][1:], [])
            server.ssh_cd(argv[3][1:], 'IN_DOCKER_HOME=' + config.HOME + ' ' + ' '.join(escape(argv)))
	    server.ssh("sed -i.bak -e 's#CMAKE_MAKE_PROGRAM:FILEPATH=.*#CMAKE_MAKE_PROGRAM:FILEPATH={make}#' {cwd}/CMakeCache.txt".format(make=config.MAKE, cwd=local_cwd))
	    server.ssh("sed -i.bak -e 's#CMAKE_C_COMPILER:FILEPATH=.*#CMAKE_C_COMPILER:FILEPATH={cc}#' {cwd}/CMakeCache.txt".format(cc=config.CC, cwd=local_cwd))
	    server.ssh("sed -i.bak -e 's#CMAKE_CXX_COMPILER:FILEPATH=.*#CMAKE_CXX_COMPILER:FILEPATH={cxx}#' {cwd}/CMakeCache.txt".format(cxx=config.CXX, cwd=local_cwd))
            server.download(argv[3][1:], argv[3], [])
            server.ssh('rm -rf private')

if __name__ == '__main__':
    main()
