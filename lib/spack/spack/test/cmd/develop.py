# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import pytest
import os
import llnl.util.filesystem as fs

import spack.spec
import spack.environment as ev
from spack.main import SpackCommand

develop = SpackCommand('develop')
env = SpackCommand('env')


@pytest.mark.usefixtures('mutable_mock_env_path', 'mock_packages')
class TestDevelop(object):
    def check_develop(self, env, spec, path=None):
        path = path or spec.name

        # check in memory representation
        assert spec.name in env.dev_specs
        dev_specs_entry = env.dev_specs[spec.name]
        assert dev_specs_entry['path'] == path
        assert dev_specs_entry['spec'] == str(spec)

        # check yaml representation
        yaml = ev.config_dict(env.yaml)
        assert spec.name in yaml['develop']
        yaml_entry = yaml['develop'][spec.name]
        assert yaml_entry['spec'] == str(spec)
        if path == spec.name:
            # default paths aren't written out
            assert 'path' not in yaml_entry
        else:
            assert yaml_entry['path'] == path

    def test_develop_no_path_no_clone(self):
        env('create', 'test')
        with ev.read('test') as e:
            # develop checks that the path exists
            fs.mkdirp(os.path.join(e.path, 'mpich'))
            develop('--no-clone', 'mpich@1.0')
            self.check_develop(e, spack.spec.Spec('mpich@1.0'))

    def test_develop_no_clone(self, tmpdir):
        env('create', 'test')
        with ev.read('test') as e:
            develop('--no-clone', '-p', str(tmpdir), 'mpich@1.0')
            self.check_develop(e, spack.spec.Spec('mpich@1.0'), str(tmpdir))