# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.


"""Tests for all IBMQ backends."""

from unittest import skip

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.providers.exceptions import QiskitBackendNotFoundError
from qiskit.providers.ibmq import IBMQ
from qiskit.qobj import QobjHeader
from qiskit.test import QiskitTestCase, requires_qe_access, slow_test
from qiskit.tools.compiler import compile


class TestIBMQBackends(QiskitTestCase):
    """Tests for all the IBMQ backends."""
    def setUp(self):
        super().setUp()

        qr = QuantumRegister(1)
        cr = ClassicalRegister(1)
        self.qc1 = QuantumCircuit(qr, cr, name='circuit0')
        self.qc1.h(qr[0])
        self.qc1.measure(qr, cr)

    @requires_qe_access
    def test_remote_backends_exist(self, qe_token, qe_url):
        """Test if there are remote backends."""
        IBMQ.enable_account(qe_token, qe_url)
        remotes = IBMQ.backends()
        self.assertTrue(len(remotes) > 0)

    @requires_qe_access
    def test_remote_backends_exist_real_device(self, qe_token, qe_url):
        """Test if there are remote backends that are devices."""
        IBMQ.enable_account(qe_token, qe_url)
        remotes = IBMQ.backends(simulator=False)
        self.assertTrue(remotes)

    @requires_qe_access
    def test_remote_backends_exist_simulator(self, qe_token, qe_url):
        """Test if there are remote backends that are simulators."""
        IBMQ.enable_account(qe_token, qe_url)
        remotes = IBMQ.backends(simulator=True)
        self.assertTrue(remotes)

    @requires_qe_access
    def test_remote_backend_status(self, qe_token, qe_url):
        """Test backend_status."""
        IBMQ.enable_account(qe_token, qe_url)
        for backend in IBMQ.backends():
            _ = backend.status()

    @requires_qe_access
    def test_remote_backend_configuration(self, qe_token, qe_url):
        """Test backend configuration."""
        IBMQ.enable_account(qe_token, qe_url)
        remotes = IBMQ.backends()
        for backend in remotes:
            _ = backend.configuration()

    @requires_qe_access
    def test_remote_backend_properties(self, qe_token, qe_url):
        """Test backend properties."""
        IBMQ.enable_account(qe_token, qe_url)
        remotes = IBMQ.backends(simulator=False)
        for backend in remotes:
            properties = backend.properties()
            if backend.configuration().simulator:
                self.assertEqual(properties, None)

    @requires_qe_access
    @skip('Skipping until support in production API')
    def test_remote_backend_defaults(self, qe_token, qe_url):
        """Test backend pulse defaults."""
        IBMQ.enable_account(qe_token, qe_url)
        remotes = IBMQ.backends(simulator=False)
        for backend in remotes:
            _ = backend.defaults()

    @requires_qe_access
    def test_qobj_headers_in_result_sims(self, qe_token, qe_url):
        """Test that the qobj headers are passed onto the results for sims."""
        IBMQ.enable_account(qe_token, qe_url)
        backends = IBMQ.backends(simulator=True)

        custom_qobj_header = {'x': 1, 'y': [1, 2, 3], 'z': {'a': 4}}

        for backend in backends:
            with self.subTest(backend=backend):
                qobj = compile(self.qc1, backend)

                # Update the Qobj header.
                qobj.header = QobjHeader.from_dict(custom_qobj_header)
                # Update the Qobj.experiment header.
                qobj.experiments[0].header.some_field = 'extra info'

                result = backend.run(qobj).result()
                self.assertEqual(result.header.to_dict(), custom_qobj_header)
                self.assertEqual(result.results[0].header.some_field,
                                 'extra info')

    @slow_test
    @requires_qe_access
    def test_qobj_headers_in_result_devices(self, qe_token, qe_url):
        """Test that the qobj headers are passed onto the results for devices."""
        IBMQ.enable_account(qe_token, qe_url)
        backends = IBMQ.backends(simulator=False)

        custom_qobj_header = {'x': 1, 'y': [1, 2, 3], 'z': {'a': 4}}

        for backend in backends:
            with self.subTest(backend=backend):
                qobj = compile(self.qc1, backend)

                # Update the Qobj header.
                qobj.header = QobjHeader.from_dict(custom_qobj_header)
                # Update the Qobj.experiment header.
                qobj.experiments[0].header.some_field = 'extra info'

                result = backend.run(qobj).result()
                self.assertEqual(result.header.to_dict(), custom_qobj_header)
                self.assertEqual(result.results[0].header.some_field,
                                 'extra info')

    @requires_qe_access
    def test_aliases(self, qe_token, qe_url):
        """Test that display names of devices map the regular names."""
        IBMQ.enable_account(qe_token, qe_url)
        aliased_names = IBMQ._aliased_backend_names()

        for display_name, backend_name in aliased_names.items():
            with self.subTest(display_name=display_name,
                              backend_name=backend_name):
                try:
                    backend_by_name = IBMQ.get_backend(backend_name)
                except QiskitBackendNotFoundError:
                    # The real name of the backend might not exist
                    pass
                else:
                    backend_by_display_name = IBMQ.get_backend(display_name)
                    self.assertEqual(backend_by_name, backend_by_display_name)
                    self.assertEqual(backend_by_display_name.name(), backend_name)
