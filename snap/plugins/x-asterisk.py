import os
import logging
import shutil
import re
import subprocess

import snapcraft
from snapcraft.plugins import dump

logger = logging.getLogger(__name__)


class AsteriskPlugin(dump.DumpPlugin):

    def __init__(self, name, options, project):
        super().__init__(name, options, project)

    def run(self, cmd, cwd=None, **kwargs):
        envi = os.environ.copy()
        envi['CFLAGS'] = '-O2'

        super().run(cmd, cwd=cwd, **kwargs)

    def build(self):
        super().build()

        if self.extensions:
            logger.info('Building PHP extensions...')

        for extension in self.extensions:
            extension_source_directory = os.path.join(
                extension.extension_directory, 'src')
            extension_build_directory = os.path.join(
                extension.extension_directory, 'build')

            if os.path.exists(extension_build_directory):
                shutil.rmtree(extension_build_directory)

            shutil.copytree(extension_source_directory, extension_build_directory)

            self.run(['{}/phpize'.format(os.path.join(self.installdir, 'bin'))],
                     cwd=extension_build_directory)
            self.run(['./configure'] + extension.configflags,
                     cwd=extension_build_directory)
            self.run(['make', '-j{}'.format(
                self.project.parallel_build_count)],
                cwd=extension_build_directory)
            self.run(['make', 'install'], cwd=extension_build_directory)
