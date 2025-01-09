from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

class TestMyModule(TransactionCase):

    def setUp(self):
        super(TestMyModule, self).setUp()
        # Khởi tạo dữ liệu hoặc đối tượng cần kiểm thử
        self.model = self.env['my.model']
        self.record = self.model.create({
            'name': 'Test Record',
            'field': 'Value'
        })

    def test_record_creation(self):
        """Kiểm tra việc tạo bản ghi"""
        self.assertTrue(self.record, "Record should be created")
        self.assertEqual(self.record.name, 'Test Record', "Name should match the input")

    def test_field_update(self):
        """Kiểm tra cập nhật trường"""
        self.record.write({'field': 'New Value'})
        self.assertEqual(self.record.field, 'New Value', "Field value should be updated")

    def test_invalid_input(self):
        """Kiểm tra nhập liệu không hợp lệ"""
        with self.assertRaises(ValueError):
            self.model.create({'field': 'Invalid Input'})
            
    def test_access_rights(self):
        """Kiểm tra quyền truy cập"""
        with self.assertRaises(AccessError):
            self.model.sudo(self.env.ref('base.public_user')).create({
                'name': 'Unauthorized Record'
            })
                
    def test_sql_injection(self):
        """Kiểm tra SQL Injection"""
        with self.assertRaises(Exception):  # Thay Exception bằng lỗi cụ thể nếu biết
            self.env.cr.execute("SELECT * FROM my_model WHERE name = '%s'" % "'; DROP TABLE my_model; --")

    def test_logging_sensitive_data(self):
        """Kiểm tra ghi nhật ký dữ liệu nhạy cảm"""
        log_message = self.env['ir.logging'].search([('message', 'ilike', 'Sensitive')])
        self.assertFalse(log_message, "Logs should not contain sensitive data")


