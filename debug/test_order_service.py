import unittest
from unittest.mock import Mock, patch
from order_service import (
    Order,
    InventoryService,
    PaymentGateway,
    InventoryShortageError,
    PaymentFailedError,
    InvalidOrderError
)

class TestOrderService(unittest.TestCase):
    def setUp(self):
        # Create mock services
        self.mock_inventory = Mock(spec=InventoryService)
        self.mock_payment = Mock(spec=PaymentGateway)
        
        # Default order setups
        self.regular_order = Order(
            inventory_service=self.mock_inventory,
            payment_gateway=self.mock_payment,
            customer_email="regular@example.com",
            is_vip=False
        )
        self.vip_order = Order(
            inventory_service=self.mock_inventory,
            payment_gateway=self.mock_payment,
            customer_email="vip@example.com",
            is_vip=True
        )

    def test_add_item_success(self):
        self.regular_order.add_item("prod-1", 10.0, 2)
        self.assertIn("prod-1", self.regular_order.items)
        self.assertEqual(self.regular_order.items["prod-1"]["price"], 10.0)
        self.assertEqual(self.regular_order.items["prod-1"]["qty"], 2)

    def test_add_item_increment_quantity(self):
        self.regular_order.add_item("prod-1", 10.0, 2)
        self.regular_order.add_item("prod-1", 10.0, 3)
        self.assertEqual(self.regular_order.items["prod-1"]["qty"], 5)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError) as ctx:
            self.regular_order.add_item("prod-1", -5.0, 1)
        self.assertEqual(str(ctx.exception), "Price cannot be negative")

    def test_add_item_zero_or_negative_quantity(self):
        with self.assertRaises(ValueError) as ctx1:
            self.regular_order.add_item("prod-1", 10.0, 0)
        self.assertEqual(str(ctx1.exception), "Quantity must be greater than zero")

        with self.assertRaises(ValueError) as ctx2:
            self.regular_order.add_item("prod-1", 10.0, -1)
        self.assertEqual(str(ctx2.exception), "Quantity must be greater than zero")

    def test_remove_item(self):
        self.regular_order.add_item("prod-1", 10.0, 2)
        self.regular_order.remove_item("prod-1")
        self.assertNotIn("prod-1", self.regular_order.items)

    def test_remove_non_existent_item(self):
        # Should not raise any error
        self.regular_order.remove_item("non-existent")

    def test_total_price(self):
        self.assertEqual(self.regular_order.total_price, 0.0)
        self.regular_order.add_item("prod-1", 10.0, 2)  # 20.0
        self.regular_order.add_item("prod-2", 15.0, 3)  # 45.0
        self.assertEqual(self.regular_order.total_price, 65.0)

    def test_apply_discount_regular_no_discount(self):
        self.regular_order.add_item("prod-1", 50.0, 2)  # Total 100.0
        self.assertEqual(self.regular_order.apply_discount(), 100.0)

    def test_apply_discount_regular_with_discount(self):
        self.regular_order.add_item("prod-1", 50.0, 3)  # Total 150.0
        # 10% discount: 150.0 * 0.9 = 135.0
        self.assertEqual(self.regular_order.apply_discount(), 135.0)

    def test_apply_discount_vip(self):
        self.vip_order.add_item("prod-1", 50.0, 1)  # Total 50.0
        # 20% discount: 50.0 * 0.8 = 40.0
        self.assertEqual(self.vip_order.apply_discount(), 40.0)

    def test_checkout_empty_cart(self):
        with self.assertRaises(InvalidOrderError) as ctx:
            self.regular_order.checkout()
        self.assertEqual(str(ctx.exception), "Cannot checkout an empty cart")

    def test_checkout_inventory_shortage(self):
        self.regular_order.add_item("prod-1", 50.0, 3)
        self.mock_inventory.get_stock.return_value = 2  # Less than 3

        with self.assertRaises(InventoryShortageError) as ctx:
            self.regular_order.checkout()
        self.assertEqual(str(ctx.exception), "Not enough stock for prod-1")
        
        # Verify no payments were charged and no stock was decremented
        self.mock_payment.charge.assert_not_called()
        self.mock_inventory.decrement_stock.assert_not_called()

    def test_checkout_payment_failed(self):
        self.regular_order.add_item("prod-1", 50.0, 2)  # Total 100.0
        self.mock_inventory.get_stock.return_value = 10
        self.mock_payment.charge.return_value = False  # Payment declined

        with self.assertRaises(PaymentFailedError) as ctx:
            self.regular_order.checkout()
        self.assertEqual(str(ctx.exception), "Transaction declined by gateway")

        # Verify charge was attempted but stock was not decremented
        self.mock_payment.charge.assert_called_once_with(100.0, "USD")
        self.mock_inventory.decrement_stock.assert_not_called()

    def test_checkout_payment_gateway_exception(self):
        self.regular_order.add_item("prod-1", 50.0, 2)  # Total 100.0
        self.mock_inventory.get_stock.return_value = 10
        self.mock_payment.charge.side_effect = Exception("Network timeout")

        with self.assertRaises(PaymentFailedError) as ctx:
            self.regular_order.checkout()
        self.assertIn("Payment gateway error: Network timeout", str(ctx.exception))

        # Verify charge was attempted but stock was not decremented
        self.mock_payment.charge.assert_called_once_with(100.0, "USD")
        self.mock_inventory.decrement_stock.assert_not_called()

    def test_checkout_success(self):
        self.regular_order.add_item("prod-1", 50.0, 2)  # Total 100.0
        self.regular_order.add_item("prod-2", 20.0, 1)  # Total 120.0 (Regular discount applies: 120 * 0.9 = 108)
        
        # Mock responses
        self.mock_inventory.get_stock.side_effect = lambda pid: 10 if pid in ["prod-1", "prod-2"] else 0
        self.mock_payment.charge.return_value = True

        result = self.regular_order.checkout()

        self.assertEqual(result, {"status": "success", "charged_amount": 108.0})
        self.assertTrue(self.regular_order.is_paid)
        self.assertEqual(self.regular_order.status, "COMPLETED")

        # Verify payment charge
        self.mock_payment.charge.assert_called_once_with(108.0, "USD")

        # Verify stock decrements
        self.mock_inventory.decrement_stock.assert_any_call("prod-1", 2)
        self.mock_inventory.decrement_stock.assert_any_call("prod-2", 1)
        self.assertEqual(self.mock_inventory.decrement_stock.call_count, 2)

if __name__ == "__main__":
    unittest.main()
