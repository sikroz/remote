#!/usr/local/bin/python3
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
    cwd = os.getcwd()
    log = open('/tmp/cmd.log', 'a')
    log.write('argv: ' + str(sys.argv) + '\n')
    log.write('cwd: ' + cwd + '\n')
    log.close()

    argv = sys.argv
    argv0 = argv[0]
    argv0 = argv0.split('/')[-1]
    argv[0] = argv0

    if cwd.startswith(config.SRC):
        if os.path.exists(os.path.join(cwd, '..', 'conanfile.txt')) or os.path.exists(os.path.join(cwd, '..', 'conanfile.py')):
            parent = os.path.normpath(os.path.join(cwd, '..'))
        else:
            parent = cwd

        upload_exclude = ['.git', '.venv', '.vscode', 'build']
        if os.path.exists(os.path.join(parent, 'cmake-build-debug')):
            server.ssh('mkdir -p ' + os.path.join(parent, 'cmake-build-debug'))
            upload_exclude.append('cmake-build-debug')
            
        server.upload(parent, upload_exclude)

        argv.insert(0, 'CXX=clang++')
        argv.insert(0, 'CC=clang')

        if argv0 == 'conan':
            #server.upload(os.path.join(config.CONANHOME, '.conan'), ['data'])
            argv.insert(0, 'HOME=' + config.CONANHOME)
            server.ssh_cd(cwd, ' '.join(escape(argv)))
            if 'info' in argv:
                return
            server.download(os.path.join(config.CONANHOME, '.conan'), ['lib'])
        elif argv0 == 'cmake':
            #server.upload(os.path.join(config.CONANHOME, '.conan'), ['data'])
            server.upload(os.path.normpath(os.path.join(cwd, '..')), upload_exclude)
            if '--build' not in argv:
                cmake_index = argv.index('cmake')
                argv.insert(cmake_index + 1, '-DCMAKE_CXX_STANDARD=17')
                argv.insert(cmake_index + 1, '-DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS} -stdlib=libc++')
            server.ssh_cd(cwd, ' '.join(escape(argv)))
        elif argv0 in ('make', 'ninja'):
            server.ssh_cd(cwd, ' '.join(escape(argv)))

        if parent != cwd:
            server.download(cwd, ['.ssh'])
    else:
        if argv[1] == '-version':
            server.ssh(' '.join(escape(argv)))
        elif len(argv) == 4 and argv[3].startswith('/private/'):
            server.upload(argv[3], [])
            server.ssh_cd(cwd, ' '.join(escape(argv)))
            server.ssh("sed -i.bak -e 's#CMAKE_MAKE_PROGRAM:FILEPATH=.*#CMAKE_MAKE_PROGRAM:FILEPATH={make}#' {cwd}/CMakeCache.txt".format(make=config.MAKE, cwd=cwd))
            server.ssh("sed -i.bak -e 's#CMAKE_C_COMPILER:FILEPATH=.*#CMAKE_C_COMPILER:FILEPATH={cc}#' {cwd}/CMakeCache.txt".format(cc=config.CC, cwd=cwd))
            server.ssh("sed -i.bak -e 's#CMAKE_CXX_COMPILER:FILEPATH=.*#CMAKE_CXX_COMPILER:FILEPATH={cxx}#' {cwd}/CMakeCache.txt".format(cxx=config.CXX, cwd=cwd))
            server.download(argv[3], [])
            server.ssh('rm -rf ' + argv[3])

if __name__ == '__main__':
    main()
