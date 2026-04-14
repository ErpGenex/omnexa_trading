from frappe.tests.utils import FrappeTestCase

from omnexa_trading import hooks, license_gate


class TestTradingLicenseSmoke(FrappeTestCase):
	def test_license_gate_is_wired(self):
		self.assertEqual(hooks.before_request, ["omnexa_trading.license_gate.before_request"])
		self.assertEqual(license_gate._APP, "omnexa_trading")
