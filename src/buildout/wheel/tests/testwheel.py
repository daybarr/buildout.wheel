import gc
import os
import shutil
import sys
import unittest
import pkg_resources
import zc.buildout.easy_install
import zc.buildout.testing


class Buildout(object):
    """ Object to pass into the `load()` entry point during tests
    """


class BuildoutWheelTests(unittest.TestCase):

    @property
    def globs(self):
        return self.__dict__

    def setUp(self):
        self.here = os.path.dirname(__file__)
        self.fake_buildout = None
        zc.buildout.testing.buildoutSetUp(self)

    def tearDown(self):
        if self.fake_buildout:
            pkg_resources.load_entry_point(
                'buildout.wheel', 'zc.buildout.unloadextension', 'wheel'
            )(self.fake_buildout)

            # For Windows, have to force gc to close handle on '.whl' file
            # prior to the rmtree done by buildoutTearDown
            self.fake_buildout = None
            gc.collect()

        zc.buildout.testing.buildoutTearDown(self)
        os.chdir(self.here)

    def test_install_wheels(self):
        join = os.path.join
        eggs = self.tmpdir('sample_eggs')
        build = self.tmpdir('build')
        shutil.copytree(join(self.here, 'samples'), join(build, 'samples'))
        ws = zc.buildout.easy_install.install(
            ['setuptools', 'wheel'], None, check_picked=False, path=sys.path)
        py = zc.buildout.easy_install.scripts(
            [], ws, sys.executable, dest=build, interpreter='py')
        os.chdir(join(build, 'samples', 'demo'))
        zc.buildout.easy_install.call_subprocess(
            py + ['setup.py', 'bdist_wheel', '-d', eggs])
        os.chdir(join('..', 'extdemo'))
        zc.buildout.easy_install.call_subprocess(
            py + ['setup.py', 'bdist_wheel', '-d', eggs])
        os.chdir(join('..'))

        buildout = Buildout()
        pkg_resources.load_entry_point(
            'buildout.wheel', 'zc.buildout.extension', 'wheel')(buildout)
        self.fake_buildout = buildout

        ws = zc.buildout.easy_install.install(
            ['demo', 'extdemo'],
            join(self.sample_buildout, 'eggs'),
            index=eggs,
            check_picked=False,
            path=sys.path)
        py = zc.buildout.easy_install.scripts(
            [], ws, sys.executable, dest=join(self.sample_buildout, 'bin'),
            interpreter='py')
        zc.buildout.easy_install.call_subprocess(py + ['getvals.py'])
        with open('vals') as f:
            self.assertEqual('1 42', f.read())
